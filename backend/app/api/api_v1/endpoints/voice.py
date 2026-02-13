# backend/app/api/api_v1/endpoints/voice.py
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import Optional, Dict, Any
import tempfile
import os
import logging

from app.services.voice_service import voice_service
from app.services.consultation_service import consultation_service
from app.services.report_service import report_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/speech-to-text")
async def convert_speech_to_text(
    audio_file: UploadFile = File(...),
    language: str = Form("en")
) -> Dict[str, Any]:
    """Convert speech audio to text"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            content = await audio_file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Convert speech to text
            result = await voice_service.speech_to_text(temp_file_path, language)
            
            if not result['success']:
                raise HTTPException(
                    status_code=400,
                    detail=result.get('error', 'Speech-to-text conversion failed')
                )
            
            return {
                "success": True,
                "text": result['text'],
                "language": result['language'],
                "confidence": result.get('confidence', 0.0),
                "method": result.get('method', 'unknown')
            }
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Speech-to-text error: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@router.post("/text-to-speech")
async def convert_text_to_speech(
    text: str = Form(...),
    language: str = Form("en"),
    voice_type: str = Form("female")
) -> Dict[str, Any]:
    """Convert text to speech audio"""
    try:
        if not text.strip():
            raise HTTPException(status_code=400, detail="Empty text provided")
        
        # Convert text to speech
        result = await voice_service.text_to_speech(text, language, voice_type)
        
        if not result['success']:
            raise HTTPException(
                status_code=400,
                detail=result.get('error', 'Text-to-speech conversion failed')
            )
        
        return {
            "success": True,
            "audio_path": result['audio_path'],
            "language": result['language'],
            "voice_type": result['voice_type'],
            "duration": result.get('duration', 0.0),
            "method": result.get('method', 'unknown'),
            "note": result.get('note', '')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Text-to-speech error: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@router.post("/voice-consultation")
async def voice_guided_consultation(
    audio_file: UploadFile = File(...),
    language: str = Form("en"),
    patient_age: int = Form(30),
    patient_gender: str = Form("")
) -> Dict[str, Any]:
    """Complete voice-based consultation"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            content = await audio_file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Process voice consultation
            result = await voice_service.process_voice_consultation(temp_file_path, language)
            
            if not result['success']:
                raise HTTPException(
                    status_code=400,
                    detail=result.get('error', 'Voice consultation processing failed')
                )
            
            # Create consultation with extracted data
            consultation_data = result['consultation_data']
            consultation_data['patient_info']['age'] = patient_age
            consultation_data['patient_info']['gender'] = patient_gender
            
            # Create consultation session
            consultation = await consultation_service.create_consultation(
                consultation_data['patient_info'], language
            )
            
            # Add symptom analysis if symptoms were found
            if consultation_data['symptoms']:
                consultation = await consultation_service.add_symptom_analysis(
                    consultation, consultation_data['symptoms']
                )
            
            return {
                "success": True,
                "consultation_id": consultation['consultation_id'],
                "transcribed_text": result['transcribed_text'],
                "extracted_symptoms": consultation_data['symptoms'],
                "language": result['language'],
                "confidence": result.get('confidence', 0.0)
            }
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice consultation error: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@router.post("/voice-symptoms")
async def voice_symptom_input(
    audio_file: UploadFile = File(...),
    language: str = Form("en")
) -> Dict[str, Any]:
    """Extract symptoms from voice description"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            content = await audio_file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Process voice for symptoms
            result = await voice_service.process_voice_consultation(temp_file_path, language)
            
            if not result['success']:
                error_msg = result.get('error', 'Voice symptom extraction failed')
                logger.warning(f"Voice processing failed: {error_msg}")
                # Return error but don't raise exception - let frontend handle fallback
                return {
                    "success": False,
                    "error": error_msg,
                    "original_text": "",
                    "extracted_symptoms": [],
                    "language": language,
                    "confidence": 0.0
                }
            
            return {
                "success": True,
                "original_text": result.get('transcribed_text', ''),
                "extracted_symptoms": result.get('consultation_data', {}).get('symptoms', []),
                "language": result.get('language', language),
                "confidence": result.get('confidence', 0.0),
                "parsing_method": result.get('consultation_data', {}).get('parsing_method', 'unknown')
            }
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice symptom extraction error: {e}", exc_info=True)
        # Return error response instead of raising exception
        return {
            "success": False,
            "error": str(e),
            "original_text": "",
            "extracted_symptoms": [],
            "language": language,
            "confidence": 0.0
        }

@router.post("/extract-symptoms-from-text")
async def extract_symptoms_from_text(
    text: str = Form(...),
    language: str = Form("en")
) -> Dict[str, Any]:
    """Extract symptoms from text transcript (no audio file needed)"""
    try:
        if not text.strip():
            return {
                "success": False,
                "error": "Empty text provided",
                "extracted_symptoms": [],
                "confidence": 0.0
            }
        
        # Use voice service's text parsing method
        consultation_data = voice_service._parse_consultation_text(text, language)
        
        return {
            "success": True,
            "original_text": text,
            "extracted_symptoms": consultation_data.get('symptoms', []),
            "language": language,
            "confidence": 0.75,  # Text-based extraction confidence
            "parsing_method": "keyword_matching"
        }
        
    except Exception as e:
        logger.error(f"Text symptom extraction error: {e}")
        return {
            "success": False,
            "error": str(e),
            "extracted_symptoms": [],
            "confidence": 0.0
        }

@router.get("/supported-languages")
async def get_supported_languages() -> Dict[str, Any]:
    """Get list of supported languages for voice processing"""
    try:
        languages = voice_service.get_supported_languages()
        
        return {
            "success": True,
            "supported_languages": languages,
            "total_count": len(languages)
        }
        
    except Exception as e:
        logger.error(f"Error getting supported languages: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get languages: {str(e)}")

@router.get("/health")
async def voice_service_health() -> Dict[str, Any]:
    """Health check for voice service"""
    try:
        health_status = await voice_service.health_check()
        return health_status
        
    except Exception as e:
        logger.error(f"Voice service health check error: {e}")
        return {
            "service": "voice_service",
            "status": "unhealthy",
            "error": str(e)
        }