"""Lógica de sesiones y mensajes del chatbot (Tarea 4.5)."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession


class SessionNotFoundError(Exception):
    pass


class SessionForbiddenError(Exception):
    pass


class ChatService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_session(self, user_id: uuid.UUID) -> ChatSession:
        session = ChatSession(user_id=user_id)
        self.db.add(session)
        await self.db.flush()
        return session

    async def _get_owned(self, session_id: uuid.UUID | str, user_id: uuid.UUID) -> ChatSession:
        session = (await self.db.execute(
            select(ChatSession).where(ChatSession.id == session_id)
        )).scalar_one_or_none()
        if session is None:
            raise SessionNotFoundError(str(session_id))
        if session.user_id != user_id:
            raise SessionForbiddenError(str(session_id))
        return session

    async def get_history(self, session_id: uuid.UUID | str, user_id: uuid.UUID) -> list[dict]:
        await self._get_owned(session_id, user_id)
        rows = (await self.db.execute(
            select(ChatMessage).where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
        )).scalars().all()
        return [{"id": str(m.id), "role": m.role, "content": m.content,
                 "created_at": m.created_at} for m in rows]

    async def add_message(self, session_id: uuid.UUID | str, role: str, content: str) -> ChatMessage:
        msg = ChatMessage(session_id=session_id, role=role, content=content)
        self.db.add(msg)
        await self.db.flush()
        return msg

    async def recent_history(self, session_id: uuid.UUID | str) -> list[dict]:
        rows = (await self.db.execute(
            select(ChatMessage).where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.desc()).limit(settings.CHATBOT_HISTORY_TURNS)
        )).scalars().all()
        return [{"role": m.role, "content": m.content} for m in reversed(rows)]

    async def close_session(self, session_id: uuid.UUID | str, user_id: uuid.UUID) -> None:
        session = await self._get_owned(session_id, user_id)
        session.ended_at = datetime.now(timezone.utc)
        await self.db.flush()
