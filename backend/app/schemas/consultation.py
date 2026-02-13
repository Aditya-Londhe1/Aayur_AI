"""
Consultation Schemas
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class ConsultationBase(BaseModel):
    """Base consultation schema"""
    consultation_type: str  # 'full', 'pulse', 'tongue', 'symptoms', 'voice'


class ConsultationCreate(ConsultationBase):
    """Schema for creating a new consultation"""
    pass


class ConsultationUpdate(BaseModel):
    """Schema for updating consultation"""
    status: Optional[str] = None  # 'in_progress', 'completed', 'cancelled'
    completed_at: Optional[datetime] = None


class Consultation(ConsultationBase):
    """Consultation schema with database fields"""
    id: int
    user_id: int
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ConsultationResponse(BaseModel):
    """Consultation response schema"""
    consultation: Consultation
    message: str = "Consultation retrieved successfully"
