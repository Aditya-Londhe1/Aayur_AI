"""
Feedback API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.feedback import Feedback

router = APIRouter()


# Pydantic schemas
class FeedbackCreate(BaseModel):
    rating: float = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    title: Optional[str] = Field(None, max_length=200)
    message: str = Field(..., min_length=10, max_length=2000)
    category: Optional[str] = Field(None, max_length=50)


class FeedbackResponse(BaseModel):
    id: int
    user_id: int
    rating: float
    title: Optional[str]
    message: str
    category: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class FeedbackWithUser(BaseModel):
    id: int
    rating: float
    title: Optional[str]
    message: str
    category: Optional[str]
    created_at: datetime
    user_name: str
    
    class Config:
        from_attributes = True


@router.post("/", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def create_feedback(
    feedback_data: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create new feedback from authenticated user
    """
    feedback = Feedback(
        user_id=current_user.id,
        rating=feedback_data.rating,
        title=feedback_data.title,
        message=feedback_data.message,
        category=feedback_data.category or "general"
    )
    
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    
    return feedback


@router.get("/my-feedback", response_model=List[FeedbackResponse])
async def get_my_feedback(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all feedback submitted by current user
    """
    feedbacks = db.query(Feedback).filter(
        Feedback.user_id == current_user.id
    ).order_by(Feedback.created_at.desc()).all()
    
    return feedbacks


@router.get("/recent", response_model=List[FeedbackWithUser])
async def get_recent_feedback(
    limit: int = 10,
    min_rating: float = 4.0,
    db: Session = Depends(get_db)
):
    """
    Get recent positive feedback (public, no auth required)
    Used for displaying testimonials
    """
    feedbacks = db.query(Feedback).join(User).filter(
        Feedback.rating >= min_rating
    ).order_by(Feedback.created_at.desc()).limit(limit).all()
    
    result = []
    for feedback in feedbacks:
        result.append({
            "id": feedback.id,
            "rating": feedback.rating,
            "title": feedback.title,
            "message": feedback.message,
            "category": feedback.category,
            "created_at": feedback.created_at,
            "user_name": feedback.user.full_name or feedback.user.username
        })
    
    return result


@router.get("/stats")
async def get_feedback_stats(
    db: Session = Depends(get_db)
):
    """
    Get feedback statistics (public)
    """
    from sqlalchemy import func
    
    stats = db.query(
        func.count(Feedback.id).label('total_count'),
        func.avg(Feedback.rating).label('average_rating'),
        func.count(func.distinct(Feedback.user_id)).label('unique_users')
    ).first()
    
    # Count by rating
    rating_distribution = db.query(
        Feedback.rating,
        func.count(Feedback.id).label('count')
    ).group_by(Feedback.rating).all()
    
    return {
        "total_feedbacks": stats.total_count or 0,
        "average_rating": round(float(stats.average_rating or 0), 2),
        "unique_users": stats.unique_users or 0,
        "rating_distribution": {str(r.rating): r.count for r in rating_distribution}
    }


@router.delete("/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_feedback(
    feedback_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete own feedback
    """
    feedback = db.query(Feedback).filter(
        Feedback.id == feedback_id,
        Feedback.user_id == current_user.id
    ).first()
    
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )
    
    db.delete(feedback)
    db.commit()
    
    return None
