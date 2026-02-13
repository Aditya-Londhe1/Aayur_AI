"""
Pulse Data Model
"""

from sqlalchemy import Column, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class PulseData(Base):
    """Pulse data model"""
    
    __tablename__ = "pulse_data"
    
    id = Column(Integer, primary_key=True, index=True)
    consultation_id = Column(Integer, ForeignKey("consultations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Pulse readings
    pulse_readings = Column(JSON, nullable=False)  # Raw pulse data
    dosha_prediction = Column(JSON)  # ML model prediction
    ayurvedic_interpretation = Column(JSON)  # Ayurvedic analysis
    
    # Timestamp
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    consultation = relationship("Consultation", back_populates="pulse_data")
    user = relationship("User", back_populates="pulse_data")
    
    def __repr__(self):
        return f"<PulseData(id={self.id}, consultation_id={self.consultation_id})>"
