"""
Voice Conversation Models
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class VoiceConversation(Base):
    """Voice assistant conversation session"""
    
    __tablename__ = "voice_conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    consultation_id = Column(Integer, ForeignKey("consultations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Session details
    session_id = Column(String(255), unique=True, index=True, nullable=False)
    language = Column(String(10), default='en')
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    consultation = relationship("Consultation", back_populates="voice_conversations")
    user = relationship("User", back_populates="voice_conversations")
    messages = relationship("VoiceMessage", back_populates="conversation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<VoiceConversation(id={self.id}, session_id={self.session_id}, language={self.language})>"


class VoiceMessage(Base):
    """Individual message in voice conversation"""
    
    __tablename__ = "voice_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("voice_conversations.id"), nullable=False)
    
    # Message details
    role = Column(String(20), nullable=False)  # 'user', 'assistant'
    content = Column(Text, nullable=False)
    original_content = Column(Text, nullable=True)  # For translations
    language = Column(String(10))
    
    # Timestamp
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    conversation = relationship("VoiceConversation", back_populates="messages")
    
    def __repr__(self):
        return f"<VoiceMessage(id={self.id}, role={self.role}, content={self.content[:50]}...)>"
