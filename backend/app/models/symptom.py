"""
Symptom Model
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Symptom(Base):
    """Symptom model"""
    
    __tablename__ = "symptoms"
    
    id = Column(Integer, primary_key=True, index=True)
    consultation_id = Column(Integer, ForeignKey("consultations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Symptom details
    symptom_name = Column(String(255), nullable=False)
    severity = Column(String(50))  # 'mild', 'moderate', 'severe'
    duration = Column(String(100))
    
    # Timestamp
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    consultation = relationship("Consultation", back_populates="symptoms")
    user = relationship("User", back_populates="symptoms")
    
    def __repr__(self):
        return f"<Symptom(id={self.id}, name={self.symptom_name}, severity={self.severity})>"
