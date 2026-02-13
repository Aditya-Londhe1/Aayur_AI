"""
Authentication Endpoints
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.services.auth_service import AuthService
from app.schemas.auth import (
    Token,
    LoginRequest,
    RegisterRequest,
    VerifyEmailRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ChangePasswordRequest,
    RefreshTokenRequest
)
from app.schemas.user import User, UserResponse
from app.models.user import User as UserModel

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user
    
    - **email**: User email (must be unique)
    - **username**: Username (must be unique)
    - **password**: Password (minimum 8 characters)
    - **full_name**: Full name (optional)
    - **phone**: Phone number (optional)
    """
    from app.services.email_service import email_service
    
    auth_service = AuthService(db)
    user, verification_token = auth_service.register_user(request)
    
    # Send verification email
    try:
        await email_service.send_verification_email(user.email, verification_token)
        message = "Registration successful! Please check your email to verify your account."
    except Exception as e:
        logger.error(f"Failed to send verification email: {e}")
        message = "Registration successful! However, we couldn't send the verification email. Please contact support."
    
    return {
        "user": user,
        "message": message
    }


@router.post("/login", response_model=Token)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login user and get access token
    
    - **email**: User email
    - **password**: User password
    """
    auth_service = AuthService(db)
    user, access_token, refresh_token = auth_service.login_user(request)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token
    
    - **refresh_token**: Valid refresh token
    """
    auth_service = AuthService(db)
    access_token, refresh_token = auth_service.refresh_access_token(request.refresh_token)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/verify-email")
async def verify_email(
    request: VerifyEmailRequest,
    db: Session = Depends(get_db)
):
    """
    Verify user email with token
    
    - **token**: Verification token from email
    """
    from app.services.email_service import email_service
    
    auth_service = AuthService(db)
    user = auth_service.verify_email(request.token)
    
    # Send welcome email
    try:
        await email_service.send_welcome_email(user.email, user.full_name or user.username)
    except Exception as e:
        logger.error(f"Failed to send welcome email: {e}")
    
    return {
        "message": "Email verified successfully!",
        "user": user
    }


@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Request password reset
    
    - **email**: User email
    """
    from app.services.email_service import email_service
    
    auth_service = AuthService(db)
    user, reset_token = auth_service.request_password_reset(request.email)
    
    # Send password reset email
    try:
        await email_service.send_password_reset_email(user.email, reset_token)
        message = "Password reset email sent! Please check your email."
    except Exception as e:
        logger.error(f"Failed to send password reset email: {e}")
        message = "We couldn't send the password reset email. Please try again later."
    
    return {
        "message": message
    }


@router.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Reset password with token
    
    - **token**: Reset token from email
    - **new_password**: New password (minimum 8 characters)
    """
    auth_service = AuthService(db)
    user = auth_service.reset_password(request.token, request.new_password)
    
    return {
        "message": "Password reset successfully!"
    }


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change user password (requires authentication)
    
    - **current_password**: Current password
    - **new_password**: New password (minimum 8 characters)
    """
    auth_service = AuthService(db)
    user = auth_service.change_password(current_user, request.current_password, request.new_password)
    
    return {
        "message": "Password changed successfully!"
    }


@router.get("/me", response_model=User)
async def get_current_user_info(
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get current authenticated user information
    """
    return current_user


@router.post("/logout")
async def logout(
    current_user: UserModel = Depends(get_current_user)
):
    """
    Logout user (client should discard tokens)
    
    Note: JWT tokens are stateless, so logout is handled client-side.
    For production, implement token blacklisting.
    """
    return {
        "message": "Logged out successfully"
    }


@router.post("/resend-verification")
async def resend_verification(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Resend verification email to current user
    
    Only works if user is not already verified
    """
    from app.services.email_service import email_service
    from app.core.security import create_verification_token
    
    # Check if already verified
    if current_user.is_verified:
        return {
            "message": "Email is already verified"
        }
    
    # Generate new verification token
    verification_token = create_verification_token(current_user.email)
    
    # Update user's verification token
    current_user.verification_token = verification_token
    db.commit()
    
    # Send verification email
    try:
        await email_service.send_verification_email(current_user.email, verification_token)
        message = "Verification email sent! Please check your email."
    except Exception as e:
        logger.error(f"Failed to send verification email: {e}")
        message = "Failed to send verification email. Please try again later."
    
    return {
        "message": message
    }
