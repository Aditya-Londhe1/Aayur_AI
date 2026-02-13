"""
Tongue Image Model
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class TongueImage(Base):
    """Tongue image model"""
    
    __tablename__ = "tongue_images"
    
    id = Column(Integer, primary_key=True, index=True)
    consultation_id = Column(Integer, ForeignKey("consultations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Image data
    image_path = Column(String(500), nullable=False)
    dosha_prediction = Column(JSON)  # ML model prediction
    features = Column(JSON)  # Extracted features
    
    # Timestamp
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    consultation = relationship("Consultation", back_populates="tongue_images")
    user = relationship("User", back_populates="tongue_images")
    
    def __repr__(self):
        return f"<TongueImage(id={self.id}, consultation_id={self.consultation_id})>"
