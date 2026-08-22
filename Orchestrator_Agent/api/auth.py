"""
Authentication Router

Project: Educational Content Generator AI
Module: Orchestrator Agent (Gateway)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.connection import get_db
from database.crud import get_user_by_email, get_user_by_username, create_user, verify_password
from database.schemas import UserCreate, UserLogin, UserResponse, Token
from utils.security import create_access_token, get_current_user
from database.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=UserResponse)
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    """Registers a new student user."""
    # Check if email is already taken
    db_user = get_user_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists."
        )
    
    # Check if username is already taken
    db_user = get_user_by_username(db, username=user_in.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this username already exists."
        )
    
    return create_user(db=db, user=user_in)


@router.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    """Authenticates a user and returns a JWT access token."""
    # Find user by email
    user = get_user_by_email(db, email=user_in.email)
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password."
        )
    
    # Issue JWT token
    access_token = create_access_token(data={"sub": str(user.id)})
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Retrieves current logged-in user profile details."""
    return current_user
