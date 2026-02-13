"""
Authentication Service
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    create_verification_token,
    create_reset_token,
    decode_token
)


class AuthService:
    """Authentication service for user registration, login, and token management"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def register_user(self, request: RegisterRequest) -> Tuple[User, str]:
        """
        Register a new user
        
        Args:
            request: Registration request data
            
        Returns:
            Tuple of (user, verification_token)
            
        Raises:
            HTTPException: If email or username already exists
        """
        # Check if email already exists
        existing_user = self.db.query(User).filter(User.email == request.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if username already exists
        existing_username = self.db.query(User).filter(User.username == request.username).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Hash password
        password_hash = get_password_hash(request.password)
        
        # Create verification token
        verification_token = create_verification_token(request.email)
        
        # Create user
        user = User(
            email=request.email,
            username=request.username,
            password_hash=password_hash,
            full_name=request.full_name,
            phone=request.phone,
            verification_token=verification_token,
            is_verified=False  # Require email verification
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user, verification_token
    
    def login_user(self, request: LoginRequest) -> Tuple[User, str, str]:
        """
        Login user and generate tokens
        
        Args:
            request: Login request data
            
        Returns:
            Tuple of (user, access_token, refresh_token)
            
        Raises:
            HTTPException: If credentials are invalid
        """
        # Get user by email
        user = self.db.query(User).filter(User.email == request.email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Verify password
        if not verify_password(request.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        # Update last login
        user.last_login = datetime.utcnow()
        self.db.commit()
        
        # Generate tokens
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})
        
        return user, access_token, refresh_token
    
    def verify_email(self, token: str) -> User:
        """
        Verify user email with token
        
        Args:
            token: Verification token
            
        Returns:
            Verified user
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        # Decode token
        payload = decode_token(token)
        if not payload or payload.get("type") != "verification":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token"
            )
        
        # Get email from token
        email = payload.get("sub")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token payload"
            )
        
        # Get user by email and token
        user = self.db.query(User).filter(
            User.email == email,
            User.verification_token == token
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or token already used"
            )
        
        # Mark user as verified
        user.is_verified = True
        user.verification_token = None
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def request_password_reset(self, email: str) -> Tuple[User, str]:
        """
        Request password reset
        
        Args:
            email: User email
            
        Returns:
            Tuple of (user, reset_token)
            
        Raises:
            HTTPException: If user not found
        """
        # Get user by email
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Generate reset token
        reset_token = create_reset_token(email)
        
        # Save reset token
        user.reset_token = reset_token
        user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        self.db.commit()
        
        return user, reset_token
    
    def reset_password(self, token: str, new_password: str) -> User:
        """
        Reset user password with token
        
        Args:
            token: Reset token
            new_password: New password
            
        Returns:
            User with updated password
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        # Decode token
        payload = decode_token(token)
        if not payload or payload.get("type") != "reset":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        # Get email from token
        email = payload.get("sub")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token payload"
            )
        
        # Get user by email and token
        user = self.db.query(User).filter(
            User.email == email,
            User.reset_token == token
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or token already used"
            )
        
        # Check if token is expired
        if user.reset_token_expires and user.reset_token_expires < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token has expired"
            )
        
        # Update password
        user.password_hash = get_password_hash(new_password)
        user.reset_token = None
        user.reset_token_expires = None
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def refresh_access_token(self, refresh_token: str) -> Tuple[str, str]:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            Tuple of (new_access_token, new_refresh_token)
            
        Raises:
            HTTPException: If refresh token is invalid
        """
        # Decode refresh token
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user ID from token
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Verify user exists
        user = self.db.query(User).filter(User.id == int(user_id)).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Generate new tokens
        new_access_token = create_access_token({"sub": user_id})
        new_refresh_token = create_refresh_token({"sub": user_id})
        
        return new_access_token, new_refresh_token
    
    def change_password(self, user: User, current_password: str, new_password: str) -> User:
        """
        Change user password
        
        Args:
            user: Current user
            current_password: Current password
            new_password: New password
            
        Returns:
            User with updated password
            
        Raises:
            HTTPException: If current password is incorrect
        """
        # Verify current password
        if not verify_password(current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        user.password_hash = get_password_hash(new_password)
        self.db.commit()
        self.db.refresh(user)
        
        return user
