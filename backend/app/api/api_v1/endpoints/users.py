"""
User Management Endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.services.user_service import UserService
from app.schemas.user import User, UserUpdate, UserResponse
from app.models.user import User as UserModel

router = APIRouter()


@router.get("/me", response_model=User)
async def get_my_profile(
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get current user profile
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_my_profile(
    update_data: UserUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user profile
    
    - **full_name**: Full name (optional)
    - **phone**: Phone number (optional)
    - **date_of_birth**: Date of birth (optional)
    - **gender**: Gender (optional)
    """
    user_service = UserService(db)
    updated_user = user_service.update_user_profile(current_user, update_data)
    
    return {
        "user": updated_user,
        "message": "Profile updated successfully"
    }


@router.delete("/me")
async def delete_my_account(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete current user account (hard delete)
    
    Warning: This action cannot be undone!
    """
    user_service = UserService(db)
    user_service.delete_user(current_user)
    
    return {
        "message": "Account deleted successfully"
    }


@router.post("/me/deactivate")
async def deactivate_my_account(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deactivate current user account (soft delete)
    
    Account can be reactivated by contacting support
    """
    user_service = UserService(db)
    user_service.deactivate_user(current_user)
    
    return {
        "message": "Account deactivated successfully"
    }


@router.get("/{user_id}", response_model=User)
async def get_user_by_id(
    user_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user by ID (authenticated users only)
    """
    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user
