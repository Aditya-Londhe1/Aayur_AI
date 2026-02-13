
# backend/app/services/voice_service.py
import logging
from typing import Dict, Any, Optional, List
import os
import tempfile
from pathlib import Path
import json

# Import the new analyzer
from app.ai_models.voice_analysis import voice_analyzer

logger = logging.getLogger(__name__)

class VoiceService:
    """
    Advanced Voice Service for Speech-to-Text and Dosha Analysis.
    Integrates acoustic feature extraction and speech recognition.
    """
    
    def __init__(self):
        self.analyzer = voice_analyzer
        self.supported_languages = [
            "en", "hi", "ta", "te", "kn", "ml", "gu", "mr", "bn", "pa", "or"
        ]
        logger.info("VoiceService initialized with AI analysis capabilities")
    
    async def speech_to_text(self, audio_file_path: str, language: str = "en") -> Dict[str, Any]:
        """Convert speech to text using Google Speech Recognition"""
        try:
            if not os.path.exists(audio_file_path):
                return {"success": False, "error": "Audio file not found", "text": ""}
            
            # Use analyzer's transcribe method (synchronous, run in thread if needed)
            # For simplicity in this demo, running direct
            text = self.analyzer._transcribe(audio_file_path)
            
            if not text:
                 return {"success": False, "error": "Transcription returned empty", "text": ""}

            return {
                "success": True,
                "text": text,
                "language": language,
                "confidence": 0.85, # Google API doesn't always return confidence easily in simple mode
                "method": "google_speech_recognition"
            }
            
        except Exception as e:
            logger.error(f"Speech-to-text error: {e}")
            return {"success": False, "error": str(e), "text": ""}
    
    async def process_voice_consultation(self, audio_file_path: str, language: str = "en") -> Dict[str, Any]:
        """
        Process voice input for consultation:
        1. Acoustic Analysis (Dosha Detection)
        2. Speech-to-Text (Symptom Extraction)
        """
        try:
            # Run complete analysis
            analysis_result = self.analyzer.analyze(audio_file_path)
            
            if not analysis_result["success"]:
                 return {"success": False, "error": analysis_result.get("error")}

            transcribed_text = analysis_result["transcript"]
            acoustic_features = analysis_result["acoustic_features"]
            dosha_prediction = analysis_result["dosha_prediction"]
            
            # Parse symptoms from text
            consultation_data = self._parse_consultation_text(transcribed_text, language)
            
            # Enrich consultation data with Voice Dosha Analysis
            consultation_data["voice_analysis"] = {
                "dosha_prediction": dosha_prediction,
                "acoustic_features": acoustic_features
            }

            return {
                "success": True,
                "transcribed_text": transcribed_text,
                "consultation_data": consultation_data,
                "voice_analysis": dosha_prediction,
                "language": language,
                "confidence": dosha_prediction["confidence"]
            }
            
        except Exception as e:
            logger.error(f"Voice consultation processing error: {e}")
            return {"success": False, "error": str(e), "consultation_data": None}

    def _parse_consultation_text(self, text: str, language: str) -> Dict[str, Any]:
        """
        Parse consultation information from transcribed text
        """
        try:
            # Basic keyword extraction for symptoms (can be improved with NLP)
            symptom_keywords = {
                "en": ["pain", "headache", "fever", "cough", "tired", "stress", "anxiety", "stomach", "sleep", "insomnia"],
                "hi": ["दर्द", "सिरदर्द", "बुखार", "खांसी", "थकान", "तनाव", "चिंता", "पेट", "नींद"]
            }
            
            keywords = symptom_keywords.get(language, symptom_keywords["en"])
            found_symptoms = []
            text_lower = text.lower()
            
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    found_symptoms.append({
                        "name": keyword,
                        "severity": "moderate",
                        "duration": "",
                        "description": f"Mentioned in voice consultation"
                    })
            
            patient_info = {
                "age": 30,
                "consultation_method": "voice",
                "language": language
            }
            
            return {
                "symptoms": found_symptoms,
                "patient_info": patient_info,
                "raw_text": text
            }
            
        except Exception as e:
            logger.error(f"Text parsing error: {e}")
            return {
                "symptoms": [],
                "patient_info": {}, 
                "raw_text": text,
                "error": str(e)
            }
    
    async def text_to_speech(self, text: str, language: str = "en", voice_type: str = "female") -> Dict[str, Any]:
        """
        Text-to-Speech using gTTS (Google Text-to-Speech)
        
        Note: This is a basic implementation. For production, consider:
        - Google Cloud TTS for better quality
        - Caching audio files
        - Streaming audio
        """
        try:
            from gtts import gTTS
            import tempfile
            import os
            
            # Create temporary file for audio
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                temp_path = temp_file.name
            
            # Generate speech
            tts = gTTS(text=text, lang=language, slow=False)
            tts.save(temp_path)
            
            return {
                "success": True,
                "audio_path": temp_path,
                "method": "gtts",
                "language": language,
                "note": "Audio file generated. Remember to delete after use."
            }
            
        except ImportError:
            logger.warning("gTTS not installed. Install with: pip install gtts")
            return {
                "success": False,
                "error": "TTS library not installed",
                "note": "Install gTTS: pip install gtts"
            }
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_supported_languages(self) -> List[str]:
        return self.supported_languages.copy()
    
    async def health_check(self) -> Dict[str, Any]:
        return {"service": "voice_service", "status": "healthy", "backend": "librosa + speech_recognition"}

voice_service = VoiceService()