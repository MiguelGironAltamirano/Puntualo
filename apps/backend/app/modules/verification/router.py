from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.modules.auth.dependencies import get_current_user
from app.modules.verification.schemas import UploadCarnetResponse
from app.modules.verification.service import upload_carnet_side


router = APIRouter()


@router.post(
    "/carnet/{side}",
    response_model=UploadCarnetResponse,
)
async def upload_carnet(
    side: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    file_bytes = await file.read()
    return upload_carnet_side(
        db=db,
        user=current_user,
        side=side,
        content_type=file.content_type or "",
        file_bytes=file_bytes,
    )
