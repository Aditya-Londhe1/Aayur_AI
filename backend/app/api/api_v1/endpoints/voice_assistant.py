"""
Voice Assistant API Endpoints - Option A Implementation
Universal Language Support with Dual Processing
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
import uuid
import tempfile
import os

from app.services.multilingual_voice_service import multilingual_voice_service
from app.services.gemini_service import gemini_service
from app.services.multilingual_translator import multilingual_translator

logger = logging.getLogger(__name__)

router = APIRouter()

# Request/Response Models
class StartSessionRequest(BaseModel):
    language: Optional[str] = "en"

class ChatRequest(BaseModel):
    conversation_id: str
    message: str
    language: Optional[str] = None  # Auto-detect if not provided

class VoiceUploadRequest(BaseModel):
    conversation_id: Optional[str] = None
    language: Optional[str] = None  # Auto-detect if not provided

class TranslateRequest(BaseModel):
    text: str
    source_language: Optional[str] = None
    target_language: str = "en"

@router.post("/start-session")
async def start_session(request: StartSessionRequest):
    """
    Start a new voice assistant conversation session (Option A)
    
    Universal language support - accepts any language
    
    Returns:
        conversation_id: Unique conversation identifier
        message: Initial greeting from AI (in user's language)
        language: Session language
        supported_languages: List of supported languages
    """
    try:
        # Create conversation using multilingual service
        conversation_id = multilingual_voice_service._create_conversation(
            request.language or "en"
        )
        
        # Get initial greeting from Gemini
        conversation = multilingual_voice_service.get_conversation(conversation_id)
        gemini_session = gemini_service.get_session(conversation['gemini_session_id'])
        
        # Get greeting message
        greeting = "Hello! I'm here to help you with your health concerns. What brings you here today?"
        if gemini_session and gemini_session['messages']:
            greeting = gemini_session['messages'][0]['content']
        
        # Translate to user's language if needed
        if request.language and request.language != "en":
            greeting = multilingual_translator.from_english(
                greeting,
                request.language
            )
        
        logger.info(f"Started voice session: {conversation_id} in language: {request.language}")
        
        return {
            "success": True,
            "conversation_id": conversation_id,
            "message": greeting,
            "language": request.language or "en",
            "supported_languages": multilingual_voice_service.get_supported_languages()
        }
        
    except Exception as e:
        logger.error(f"Error starting session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
async def chat(request: ChatRequest):
    """
    Send message and get AI response (Option A - Dual Processing)
    
    Implements:
    - Path A: Native language conversation with Gemini
    - Path B: English translation for backend processing
    
    Args:
        conversation_id: Conversation identifier
        message: User's message (in ANY language)
        language: User's language (auto-detect if not provided)
        
    Returns:
        message: AI response (in user's language)
        english_translation: Message translated to English
        extracted_info: Symptoms and patient info extracted
        assessment_results: Analysis results if ready
    """
    try:
        logger.info(f"Chat request - Conversation: {request.conversation_id}, Message: {request.message}")
        
        # Process using multilingual voice service (Option A)
        result = await multilingual_voice_service.process_voice_input(
            text=request.message,
            conversation_id=request.conversation_id,
            detected_language=request.language
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Processing failed"))
        
        logger.info(f"Chat processed successfully for conversation: {request.conversation_id}")
        
        return {
            "success": True,
            "conversation_id": result["conversation_id"],
            "message": result["text_response"],
            "english_translation": result.get("english_translation"),
            "language": result["language"],
            "extracted_info": result.get("extracted_info", {}),
            "assessment_results": result.get("assessment_results"),
            "conversation_state": result.get("conversation_state"),
            "message_count": result.get("message_count", 0)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{session_id}")
async def get_session(session_id: str):
    """
    Get session information
    
    Returns:
        Session data including conversation history and extracted info
    """
    try:
        session = gemini_service.get_session(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "success": True,
            "session": session
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversation/{conversation_id}")
async def get_conversation(conversation_id: str):
    """
    Get conversation information (Option A)
    
    Returns:
        Conversation data including history and extracted info
    """
    try:
        conversation = multilingual_voice_service.get_conversation(conversation_id)
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return {
            "success": True,
            "conversation": conversation
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-voice")
async def upload_voice(
    audio: UploadFile = File(...),
    conversation_id: Optional[str] = None,
    language: Optional[str] = None
):
    """
    Upload voice audio file for processing (Option A)
    
    Supports:
    - Automatic language detection from speech
    - Speech-to-text conversion
    - Dual processing (native + English)
    - Complete voice consultation flow
    
    Args:
        audio: Audio file (WAV, MP3, etc.)
        conversation_id: Existing conversation ID (optional)
        language: Expected language (optional, auto-detect if not provided)
        
    Returns:
        Transcribed text, AI response, and extracted information
    """
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            content = await audio.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        logger.info(f"Processing uploaded audio file: {audio.filename}")
        
        try:
            # Process voice input using Option A
            result = await multilingual_voice_service.process_voice_input(
                audio_file_path=temp_file_path,
                conversation_id=conversation_id,
                detected_language=language
            )
            
            if not result["success"]:
                raise HTTPException(status_code=400, detail=result.get("error", "Processing failed"))
            
            return {
                "success": True,
                "conversation_id": result["conversation_id"],
                "transcribed_text": result.get("english_translation"),  # Original transcription
                "message": result["text_response"],
                "language": result["language"],
                "extracted_info": result.get("extracted_info", {}),
                "assessment_results": result.get("assessment_results"),
                "conversation_state": result.get("conversation_state")
            }
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing voice upload: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/session/{session_id}")
async def end_session(session_id: str):
    """
    End conversation session
    """
    try:
        gemini_service.end_session(session_id)
        
        return {
            "success": True,
            "message": "Session ended"
        }
        
    except Exception as e:
        logger.error(f"Error ending session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/conversation/{conversation_id}")
async def end_conversation(conversation_id: str):
    """
    End conversation (Option A)
    """
    try:
        multilingual_voice_service.end_conversation(conversation_id)
        
        return {
            "success": True,
            "message": "Conversation ended"
        }
        
    except Exception as e:
        logger.error(f"Error ending conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/translate")
async def translate(request: TranslateRequest):
    """
    Translate text between languages
    
    Useful for testing translation without full conversation
    """
    try:
        # Detect source language if not provided
        if not request.source_language:
            detection = multilingual_translator.detect_language(request.text)
            request.source_language = detection["language"]
        
        # Translate
        if request.target_language == "en":
            translated = multilingual_translator.to_english(
                request.text,
                request.source_language
            )
        else:
            # First to English, then to target
            english = multilingual_translator.to_english(
                request.text,
                request.source_language
            )
            translated = multilingual_translator.from_english(
                english,
                request.target_language
            )
        
        return {
            "success": True,
            "original_text": request.text,
            "translated_text": translated,
            "source_language": request.source_language,
            "target_language": request.target_language
        }
        
    except Exception as e:
        logger.error(f"Error translating: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/detect-language")
async def detect_language(text: str):
    """
    Detect language of text
    """
    try:
        result = multilingual_translator.detect_language(text)
        
        return {
            "success": True,
            "language": result["language"],
            "confidence": result["confidence"],
            "all_probabilities": result.get("all_probabilities", [])
        }
        
    except Exception as e:
        logger.error(f"Error detecting language: {e}")
        raise HTTPException(status_code=500, detail=str(e))
