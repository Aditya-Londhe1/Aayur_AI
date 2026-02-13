"""
Assessment Result Model
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class AssessmentResult(Base):
    """Assessment result model"""
    
    __tablename__ = "assessment_results"
    
    id = Column(Integer, primary_key=True, index=True)
    consultation_id = Column(Integer, ForeignKey("consultations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Dosha analysis
    dosha_scores = Column(JSON, nullable=False)  # {vata: 0.3, pitta: 0.5, kapha: 0.2}
    primary_dosha = Column(String(50))
    secondary_dosha = Column(String(50))
    imbalance_level = Column(String(50))
    
    # Additional data
    symptoms = Column(JSON)  # List of symptoms
    recommendations = Column(JSON)  # List of recommendations
    home_remedies = Column(JSON)  # List of remedies
    fusion_details = Column(JSON)  # Fusion engine details
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    consultation = relationship("Consultation", back_populates="assessment_results")
    user = relationship("User", back_populates="assessment_results")
    
    def __repr__(self):
        return f"<AssessmentResult(id={self.id}, primary_dosha={self.primary_dosha})>"
