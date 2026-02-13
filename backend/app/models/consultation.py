"""
Consultation Model
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Consultation(Base):
    """Consultation session model"""
    
    __tablename__ = "consultations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Consultation details
    consultation_type = Column(String(50))  # 'full', 'pulse', 'tongue', 'symptoms', 'voice'
    status = Column(String(50), default='in_progress')  # 'in_progress', 'completed', 'cancelled'
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="consultations")
    voice_conversations = relationship("VoiceConversation", back_populates="consultation", cascade="all, delete-orphan")
    assessment_results = relationship("AssessmentResult", back_populates="consultation", cascade="all, delete-orphan")
    pulse_data = relationship("PulseData", back_populates="consultation", cascade="all, delete-orphan")
    tongue_images = relationship("TongueImage", back_populates="consultation", cascade="all, delete-orphan")
    symptoms = relationship("Symptom", back_populates="consultation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Consultation(id={self.id}, user_id={self.user_id}, type={self.consultation_type}, status={self.status})>"
