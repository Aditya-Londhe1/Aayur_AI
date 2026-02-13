"""
Feedback Model
Stores user feedback and ratings
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Feedback(Base):
    """User feedback model"""
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Float, nullable=False)  # 1-5 stars
    title = Column(String(200), nullable=True)
    message = Column(Text, nullable=False)
    category = Column(String(50), nullable=True)  # e.g., "service", "accuracy", "ui", "general"
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="feedbacks")

    def __repr__(self):
        return f"<Feedback {self.id} - Rating: {self.rating} by User {self.user_id}>"
