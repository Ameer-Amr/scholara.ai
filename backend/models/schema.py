import re
from pydantic import BaseModel, EmailStr, HttpUrl, Field, field_validator
from uuid import UUID
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, Depends, Form, UploadFile, File


class OAuthAccountBase(BaseModel):
    provider: str = Field(..., examples=["google"])
    provider_user_id: str = Field(..., examples=["102938475656473829103"])

class OAuthAccountResponse(OAuthAccountBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = Field(None, max_length=100, examples=["John Doe"])

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(
        ..., 
        min_length=8, 
        max_length=64, 
        description="Plaintext password. Must be 8-64 characters and contain mix of letters, numbers, and symbols."
    )
    name: str = Field(
        ..., 
        min_length=2, 
        max_length=50, 
        examples=["Alice Smith"],
        description="The user's full name. Trailing and leading spaces will be automatically removed."
    )

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        """Trims whitespace and converts email to lowercase to prevent duplicates."""
        if isinstance(v, str):
            return v.strip().lower()
        return v

    @field_validator("name", mode="before")
    @classmethod
    def clean_name(cls, v: str) -> str:
        """Strips accidental trailing/leading spaces from the user's name."""
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("password", mode="before")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        Enforces password complexity rules:
        - At least 1 lowercase letter
        - At least 1 uppercase letter
        - At least 1 digit
        - At least 1 special character
        """
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if len(v) > 64:
            raise ValueError("Password must be at most 64 characters long.")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one digit.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character.")
        
        return v

class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="The user's account email")
    password: str = Field(..., description="The plaintext password input")
    
class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    oauth_accounts: List[OAuthAccountResponse] = []

    class Config:
        from_attributes = True
        json_encoders = {
            HttpUrl: lambda v: str(v)
        }


class DocumentCreate(BaseModel):
    subject: str

    @classmethod
    def as_form(
        cls,
        subject: str = Form(...),
    ):
        return cls(subject=subject)


class DocumentRead(BaseModel):
    subject: str
    status: str
    summary: str

    
    