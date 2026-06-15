"""Endpoints del chatbot RAG (Tarea 4.5)."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.async_session import AsyncSessionLocal, get_async_db
from app.models.user import User
from app.modules.chat.schemas import MessageIn, MessageOut, SessionOut
from app.modules.chat.service import (
    ChatService, SessionForbiddenError, SessionNotFoundError,
)
from app.modules.professors.dependencies import require_verified_user
from app.services.chatbot.orchestrator import answer_stream
from app.services.chatbot.rate_limit import check_and_increment

# El prefijo /chat se agrega en main.py al momento del montaje,
# siguiendo la convención del resto de los routers del proyecto.
router = APIRouter(tags=["chat"])


def _map_domain_error(exc: Exception) -> None:
    """Traduce errores de dominio del chat a HTTPException de FastAPI."""
    if isinstance(exc, SessionNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "SESSION_NOT_FOUND", "message": "Sesión no encontrada"},
        )
    if isinstance(exc, SessionForbiddenError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN", "message": "Sesión de otro usuario"},
        )
    raise exc


@router.post("/sessions", response_model=SessionOut, status_code=201)
async def open_session(
    current_user: User = Depends(require_verified_user),
    db: AsyncSession = Depends(get_async_db),
) -> SessionOut:
    """Abre una nueva sesión de chat para el usuario autenticado."""
    service = ChatService(db)
    session = await service.create_session(current_user.id)
    await db.commit()
    return SessionOut(session_id=str(session.id))


@router.get("/sessions/{session_id}/messages", response_model=list[MessageOut])
async def list_messages(
    session_id: uuid.UUID,
    current_user: User = Depends(require_verified_user),
    db: AsyncSession = Depends(get_async_db),
) -> list[MessageOut]:
    """Devuelve el historial de mensajes de una sesión."""
    try:
        history = await ChatService(db).get_history(session_id, current_user.id)
    except (SessionNotFoundError, SessionForbiddenError) as exc:
        _map_domain_error(exc)
    return [MessageOut(**m) for m in history]


@router.delete("/sessions/{session_id}", status_code=204)
async def close_session(
    session_id: uuid.UUID,
    current_user: User = Depends(require_verified_user),
    db: AsyncSession = Depends(get_async_db),
) -> None:
    """Cierra (marca como terminada) una sesión de chat."""
    try:
        await ChatService(db).close_session(session_id, current_user.id)
        await db.commit()
    except (SessionNotFoundError, SessionForbiddenError) as exc:
        _map_domain_error(exc)


@router.post("/sessions/{session_id}/messages")
async def post_message(
    session_id: uuid.UUID,
    body: MessageIn,
    current_user: User = Depends(require_verified_user),
    db: AsyncSession = Depends(get_async_db),
) -> StreamingResponse:
    """Envía un mensaje y retorna la respuesta del chatbot en streaming SSE."""
    if not await check_and_increment(str(current_user.id)):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "code": "RATE_LIMIT_EXCEEDED",
                "message": "Has alcanzado el límite de mensajes por hora",
            },
        )

    # Fase BD acotada: verificar ownership, persistir mensaje del usuario y cargar historial.
    service = ChatService(db)
    try:
        await service._get_owned(session_id, current_user.id)
    except (SessionNotFoundError, SessionForbiddenError) as exc:
        _map_domain_error(exc)
    await service.add_message(session_id, "user", body.content)
    history = await service.recent_history(session_id)
    await db.commit()

    async def _gen():
        # El retrieval/tools usan su propia sesión; el stream NO retiene la del request.
        chunks: list[str] = []
        async with AsyncSessionLocal() as work_db:
            async for chunk in answer_stream(
                db=work_db, user_message=body.content, history=history
            ):
                chunks.append(chunk)
                yield f"data: {chunk}\n\n"
        # Persistir el mensaje del asistente en una sesión nueva y corta.
        async with AsyncSessionLocal() as persist_db:
            await ChatService(persist_db).add_message(
                session_id, "assistant", "".join(chunks)
            )
            await persist_db.commit()
        yield "event: done\ndata: [DONE]\n\n"

    return StreamingResponse(_gen(), media_type="text/event-stream")
