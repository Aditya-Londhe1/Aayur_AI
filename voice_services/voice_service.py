# voice_services/voice_service.py
import os
import json
import asyncio
from typing import Dict, Any, Optional, BinaryIO
from datetime import datetime
import tempfile
import logging

from .speech_recognition.stt_service import SpeechToTextService
from .text_to_speech.tts_service import TextToSpeechService
from .voice_assistant.assistant_service import VoiceAssistantService
from .audio_processing.audio_utils import AudioProcessor

logger = logging.getLogger(__name__)

class AayurVoiceService:
    """Complete voice service for Aayur AI"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Initialize services
        self.stt_service = SpeechToTextService(config)
        self.tts_service = TextToSpeechService(config)
        self.assistant_service = VoiceAssistantService(config)
        self.audio_processor = AudioProcessor()
        
        # Supported languages
        self.supported_languages = {
            'en': 'English',
            'hi': 'Hindi',
            'ta': 'Tamil',
            'te': 'Telugu',
            'kn': 'Kannada',
            'ml': 'Malayalam',
            'bn': 'Bengali',
            'gu': 'Gujarati',
            'mr': 'Marathi',
            'pa': 'Punjabi',
            'ur': 'Urdu'
        }
        
        logger.info("AayurVoiceService initialized with support for 11 Indian languages")
    
    async def speech_to_text(self, audio_data: bytes, 
                           language: str = 'en',
                           context: str = 'general') -> Dict[str, Any]:
        """
        Convert speech to text with language detection
        
        Args:
            audio_data: Raw audio bytes
            language: Target language code
            context: Context for better recognition (consultation, symptoms, etc.)
        
        Returns:
            Dict with transcribed text and metadata
        """
        try:
            # Process audio (noise reduction, normalization)
            processed_audio = await self.audio_processor.process_audio(audio_data)
            
            # Detect language if not specified
            if language == 'auto':
                detected_lang = await self.stt_service.detect_language(processed_audio)
                language = detected_lang or 'en'
            
            # Convert speech to text
            result = await self.stt_service.recognize(
                audio_data=processed_audio,
                language=language,
                context=context
            )
            
            return {
                'success': True,
                'text': result['text'],
                'language': language,
                'confidence': result['confidence'],
                'alternatives': result.get('alternatives', []),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Speech recognition error: {e}")
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'language': language
            }
    
    async def text_to_speech(self, text: str, 
                           language: str = 'en',
                           voice_type: str = 'friendly',
                           speed: float = 1.0) -> Dict[str, Any]:
        """
        Convert text to speech with emotion and tone
        
        Args:
            text: Text to convert to speech
            language: Target language code
            voice_type: Type of voice (friendly, professional, soothing, authoritative)
            speed: Speech speed (0.5 to 2.0)
        
        Returns:
            Dict with audio data and metadata
        """
        try:
            # Validate language
            if language not in self.supported_languages:
                language = 'en'
            
            # Generate speech
            result = await self.tts_service.synthesize(
                text=text,
                language=language,
                voice_type=voice_type,
                speed=speed
            )
            
            return {
                'success': True,
                'audio_data': result['audio_data'],
                'audio_format': result['format'],
                'language': language,
                'voice_type': voice_type,
                'duration_seconds': result.get('duration', 0),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Text-to-speech error: {e}")
            return {
                'success': False,
                'error': str(e),
                'audio_data': None
            }
    
    async def voice_consultation(self, user_audio: bytes, 
                               consultation_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete voice-based consultation
        
        Args:
            user_audio: User's voice recording
            consultation_context: Context about the consultation
        
        Returns:
            Dict with AI response in text and audio
        """
        try:
            # Step 1: Convert user speech to text
            stt_result = await self.speech_to_text(
                user_audio,
                language=consultation_context.get('language', 'en'),
                context='consultation'
            )
            
            if not stt_result['success']:
                return {
                    'success': False,
                    'error': 'Could not understand speech',
                    'user_text': ''
                }
            
            user_text = stt_result['text']
            detected_language = stt_result['language']
            
            # Step 2: Process with voice assistant
            assistant_response = await self.assistant_service.process_query(
                user_query=user_text,
                context=consultation_context,
                language=detected_language
            )
            
            # Step 3: Convert assistant response to speech
            tts_result = await self.text_to_speech(
                text=assistant_response['text_response'],
                language=detected_language,
                voice_type=assistant_response.get('voice_type', 'friendly'),
                speed=assistant_response.get('speech_speed', 1.0)
            )
            
            return {
                'success': True,
                'user_input': {
                    'text': user_text,
                    'language': detected_language,
                    'confidence': stt_result['confidence']
                },
                'assistant_response': {
                    'text': assistant_response['text_response'],
                    'audio': tts_result['audio_data'] if tts_result['success'] else None,
                    'audio_format': tts_result.get('audio_format'),
                    'next_action': assistant_response.get('next_action'),
                    'requires_input': assistant_response.get('requires_input', False)
                },
                'consultation_step': assistant_response.get('consultation_step'),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Voice consultation error: {e}")
            return {
                'success': False,
                'error': str(e),
                'user_text': ''
            }
    
    async def generate_audio_report(self, report_data: Dict[str, Any],
                                  language: str = 'en') -> Dict[str, Any]:
        """
        Generate audio version of diagnosis report
        
        Args:
            report_data: Report data from consultation
            language: Target language for audio
        
        Returns:
            Dict with audio report
        """
        try:
            # Format report for audio
            audio_text = self._format_report_for_audio(report_data, language)
            
            # Generate speech
            tts_result = await self.text_to_speech(
                text=audio_text,
                language=language,
                voice_type='professional',
                speed=0.9  # Slightly slower for reports
            )
            
            if not tts_result['success']:
                return {
                    'success': False,
                    'error': 'Failed to generate audio report'
                }
            
            # Add chapter markers for navigation
            chapters = self._create_audio_chapters(report_data)
            
            return {
                'success': True,
                'audio_data': tts_result['audio_data'],
                'audio_format': tts_result['audio_format'],
                'duration_seconds': tts_result['duration_seconds'],
                'chapters': chapters,
                'language': language,
                'timestamp': datetime.now().isoformat(),
                'report_id': report_data.get('report_id', '')
            }
            
        except Exception as e:
            logger.error(f"Audio report generation error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def voice_symptom_input(self, audio_data: bytes,
                                language: str = 'en') -> Dict[str, Any]:
        """
        Extract symptoms from voice description
        
        Args:
            audio_data: User describing symptoms
            language: Language of description
        
        Returns:
            Dict with extracted symptoms and severity
        """
        try:
            # Convert speech to text
            stt_result = await self.speech_to_text(
                audio_data,
                language=language,
                context='medical_symptoms'
            )
            
            if not stt_result['success']:
                return {
                    'success': False,
                    'error': 'Could not understand symptom description'
                }
            
            # Extract symptoms from text
            symptom_text = stt_result['text']
            extracted_symptoms = await self._extract_symptoms_from_text(
                symptom_text,
                language
            )
            
            return {
                'success': True,
                'original_text': symptom_text,
                'extracted_symptoms': extracted_symptoms,
                'language': language,
                'confidence': stt_result['confidence']
            }
            
        except Exception as e:
            logger.error(f"Voice symptom input error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def voice_guided_tongue_capture(self, instructions_language: str = 'en') -> Dict[str, Any]:
        """
        Provide voice guidance for tongue image capture
        
        Args:
            instructions_language: Language for instructions
        
        Returns:
            Dict with audio guidance steps
        """
        try:
            # Tongue capture instructions
            instructions = [
                {
                    'text': 'Please open your mouth and extend your tongue naturally.',
                    'wait_time': 5,
                    'voice_type': 'calm'
                },
                {
                    'text': 'Make sure your tongue is relaxed, not strained.',
                    'wait_time': 3,
                    'voice_type': 'calm'
                },
                {
                    'text': 'Try to keep your tongue in the center, not tilted.',
                    'wait_time': 3,
                    'voice_type': 'calm'
                },
                {
                    'text': 'Ready? I will count down from 3. Please hold still.',
                    'wait_time': 2,
                    'voice_type': 'clear'
                },
                {
                    'text': '3... 2... 1...',
                    'wait_time': 3,
                    'voice_type': 'clear'
                },
                {
                    'text': 'Perfect! You can relax now.',
                    'wait_time': 0,
                    'voice_type': 'friendly'
                }
            ]
            
            # Generate audio for each instruction
            guidance_audio = []
            for i, instruction in enumerate(instructions):
                tts_result = await self.text_to_speech(
                    text=instruction['text'],
                    language=instructions_language,
                    voice_type=instruction['voice_type'],
                    speed=0.9
                )
                
                if tts_result['success']:
                    guidance_audio.append({
                        'step': i + 1,
                        'audio': tts_result['audio_data'],
                        'text': instruction['text'],
                        'wait_time': instruction['wait_time'],
                        'format': tts_result['audio_format']
                    })
            
            return {
                'success': True,
                'guidance_steps': guidance_audio,
                'total_steps': len(instructions),
                'language': instructions_language
            }
            
        except Exception as e:
            logger.error(f"Voice guidance error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _format_report_for_audio(self, report_data: Dict[str, Any], language: str) -> str:
        """Format text report for audio consumption"""
        # Extract key information
        patient_name = report_data.get('patient_name', 'Patient')
        dominant_dosha = report_data.get('dominant_dosha', '').capitalize()
        imbalance = report_data.get('imbalance_level', '').capitalize()
        
        # Recommendations
        dietary = report_data.get('dietary_recommendations', [])[:3]
        lifestyle = report_data.get('lifestyle_recommendations', [])[:3]
        herbs = report_data.get('herbal_recommendations', [])[:3]
        
        # Format audio text
        audio_text = f"""
        Aayur AI Diagnosis Report for {patient_name}.
        
        Your Ayurvedic analysis shows {imbalance} {dominant_dosha} imbalance.
        
        Dietary Recommendations:
        {'. '.join(dietary)}
        
        Lifestyle Changes:
        {'. '.join(lifestyle)}
        
        Herbal Remedies:
        {'. '.join(herbs)}
        
        This concludes your Aayur AI diagnosis report.
        For personalized treatment, consult a qualified Ayurvedic practitioner.
        """
        
        return audio_text.strip()
    
    def _create_audio_chapters(self, report_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create chapter markers for audio navigation"""
        chapters = [
            {
                'title': 'Introduction',
                'start_time': 0,
                'duration': 10
            },
            {
                'title': 'Dosha Analysis',
                'start_time': 10,
                'duration': 30
            },
            {
                'title': 'Dietary Recommendations',
                'start_time': 40,
                'duration': 45
            },
            {
                'title': 'Lifestyle Changes',
                'start_time': 85,
                'duration': 45
            },
            {
                'title': 'Herbal Remedies',
                'start_time': 130,
                'duration': 40
            },
            {
                'title': 'Conclusion',
                'start_time': 170,
                'duration': 20
            }
        ]
        
        return chapters
    
    async def _extract_symptoms_from_text(self, text: str, language: str) -> List[Dict[str, Any]]:
        """Extract symptoms and severity from text description"""
        # This would use NLP to extract symptoms
        # For now, return mock data
        return [
            {
                'symptom': 'headache',
                'severity': 7,
                'confidence': 0.8,
                'duration': '2 days'
            },
            {
                'symptom': 'fatigue',
                'severity': 6,
                'confidence': 0.7,
                'duration': '1 week'
            }
        ]

# Global voice service instance
voice_service = AayurVoiceService()