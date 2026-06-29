from backend.core.utils import get_current_user
from backend.models.db_models import DocumentStatus
from backend.models.db_models import Document, User
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Request
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.database import get_db
from backend.models.schema import DocumentCreate
from backend.core.database import get_db
from pathlib import Path
import aiofiles
from sqlalchemy.future import select

UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    payload: DocumentCreate = Depends(DocumentCreate.as_form),
    db: AsyncSession = Depends(get_db),
    email: str = Depends(get_current_user) 
):
    result = await db.execute(select(User).filter(User.email == email))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    unique_filename = f"{user.id}_{file.filename}" 
    destination_path = UPLOAD_DIR / unique_filename

    try:
        async with aiofiles.open(destination_path, "wb") as out_file:
            content = await file.read()
            await out_file.write(content)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to save file onto server."
        )

    new_document = Document(
        user_id=user.id,
        file_name=file.filename,
        file_path=str(destination_path),
        subject=payload.subject,
        status=DocumentStatus.PENDING,
        summary=None,
    )

    try:
        db.add(new_document)
        await db.commit()
        await db.refresh(new_document)
        return {
            "message": "Document uploaded successfully"
        }
    except Exception as e:
        await db.rollback()
        if destination_path.exists():
            destination_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register document in database."
        )

    
