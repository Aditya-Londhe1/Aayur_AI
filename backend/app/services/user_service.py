"""
User Service
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserUpdate


class UserService:
    """User management service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID
        
        Args:
            user_id: User ID
            
        Returns:
            User or None
        """
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email
        
        Args:
            email: User email
            
        Returns:
            User or None
        """
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username
        
        Args:
            username: Username
            
        Returns:
            User or None
        """
        return self.db.query(User).filter(User.username == username).first()
    
    def update_user_profile(self, user: User, update_data: UserUpdate) -> User:
        """
        Update user profile
        
        Args:
            user: User to update
            update_data: Update data
            
        Returns:
            Updated user
        """
        # Update only provided fields
        update_dict = update_data.model_dump(exclude_unset=True)
        
        for field, value in update_dict.items():
            setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def deactivate_user(self, user: User) -> User:
        """
        Deactivate user account
        
        Args:
            user: User to deactivate
            
        Returns:
            Deactivated user
        """
        user.is_active = False
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def activate_user(self, user: User) -> User:
        """
        Activate user account
        
        Args:
            user: User to activate
            
        Returns:
            Activated user
        """
        user.is_active = True
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def delete_user(self, user: User) -> None:
        """
        Delete user account (hard delete)
        
        Args:
            user: User to delete
        """
        self.db.delete(user)
        self.db.commit()
    
    def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Get all users (admin only)
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of users
        """
        return self.db.query(User).offset(skip).limit(limit).all()
