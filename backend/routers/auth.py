from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from backend.models.schema import UserCreate, UserLogin
from backend.core.database import get_db
from backend.models.db_models import User
from backend.core.utils import hash_password, verify_password
from backend.models.schema import UserResponse

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(select(User).where(User.email == payload.email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )
    
    new_user = User(
        email = payload.email,
        name = payload.name,
        hashed_password = hash_password(payload.password),
    )
    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user."
        )
    
    return {"message": "User registered successfully"}


@router.post("/login", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def login_user(
    payload: UserLogin,
    db: AsyncSession = Depends(get_db)
):

    query = (
        select(User)
        .where(User.email == payload.email)
        .options(selectinload(User.oauth_accounts))
    )
    result = await db.execute(query)
    user = result.scalars().first()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials."
        )
    
    #TODO: JWT token
    
    return user

        
    