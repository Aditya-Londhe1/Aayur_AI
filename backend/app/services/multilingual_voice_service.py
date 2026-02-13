"""
Multilingual Voice Assistant Service - Option A Implementation
Complete voice consultation with universal language support
"""

import logging
from typing import Dict, Any, List, Optional
import json
from datetime import datetime
import uuid

from app.services.gemini_service import gemini_service
from app.services.multilingual_translator import multilingual_translator
from app.services.voice_service import voice_service
from app.ai_models.symptom_analysis import symptom_analyzer

logger = logging.getLogger(__name__)

class MultilingualVoiceService:
    """
    Complete multilingual voice assistant service
    Implements Option A: Universal Language Support with Dual Processing
    """
    
    def __init__(self):
        self.translator = multilingual_translator
        self.gemini = gemini_service
        self.voice = voice_service
        self.conversations = {}  # Store active conversations
        
        logger.info("MultilingualVoiceService initialized (Option A)")
    
    async def process_voice_input(
        self,
        audio_file_path: Optional[str] = None,
        text: Optional[str] = None,
        conversation_id: Optional[str] = None,
        detected_language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process voice input in any language
        
        Implements dual processing:
        - Path A: Native language conversation with Gemini
        - Path B: English translation for backend processing
        
        Args:
            audio_file_path: Path to audio file (optional)
            text: Transcribed text (optional)
            conversation_id: Existing conversation ID (optional)
            detected_language: Pre-detected language (optional)
        
        Returns:
            Complete response with audio, text, and extracted info
        """
        try:
            # STEP 1: Speech-to-Text (if audio provided)
            if audio_file_path and not text:
                logger.info(f"Processing audio file: {audio_file_path}")
                stt_result = await self.voice.speech_to_text(
                    audio_file_path,
                    language=detected_language or "en"
                )
                
                if not stt_result["success"]:
                    return {
                        "success": False,
                        "error": stt_result.get("error", "Speech recognition failed")
                    }
                
                text = stt_result["text"]
                logger.info(f"Transcribed text: {text}")
            
            if not text:
                return {
                    "success": False,
                    "error": "No text or audio provided"
                }
            
            # STEP 2: Language Detection
            if not detected_language:
                lang_result = self.translator.detect_language(text)
                detected_language = lang_result['language']
                confidence = lang_result['confidence']
                logger.info(f"Detected language: {detected_language} (confidence: {confidence})")
            
            # STEP 3: Get or create conversation
            if not conversation_id:
                conversation_id = self._create_conversation(detected_language)
                logger.info(f"Created new conversation: {conversation_id}")
            
            conversation = self.conversations.get(conversation_id)
            if not conversation:
                return {
                    "success": False,
                    "error": "Conversation not found"
                }
            
            # STEP 4: DUAL PROCESSING
            
            # Path A: Native Language Conversation
            logger.info("Path A: Processing in native language")
            native_response = await self._process_native_conversation(
                text,
                detected_language,
                conversation
            )
            
            # Path B: English Translation for Backend
            logger.info("Path B: Translating to English for backend")
            english_text = self.translator.to_english(text, detected_language)
            logger.info(f"English translation: {english_text}")
            
            # STEP 5: Extract Information (in English)
            extracted_info = await self._extract_information(
                english_text,
                conversation
            )
            
            # STEP 6: Update Conversation
            conversation['history'].append({
                'role': 'user',
                'content': text,
                'english_translation': english_text,
                'language': detected_language,
                'timestamp': datetime.now().isoformat()
            })
            
            conversation['history'].append({
                'role': 'assistant',
                'content': native_response,
                'language': detected_language,
                'timestamp': datetime.now().isoformat()
            })
            
            # Update extracted data
            self._update_extracted_data(conversation, extracted_info)
            
            # STEP 7: Check if ready for assessment
            assessment_results = None
            if extracted_info.get('ready_for_assessment'):
                logger.info("Ready for assessment - running analysis")
                assessment_results = await self._run_assessment(
                    conversation,
                    detected_language
                )
            
            # STEP 8: Generate audio response (TTS)
            # Note: TTS implementation can be added here
            # audio_response = await self._text_to_speech(native_response, detected_language)
            
            return {
                "success": True,
                "conversation_id": conversation_id,
                "text_response": native_response,
                "english_translation": english_text,
                "language": detected_language,
                "extracted_info": extracted_info,
                "assessment_results": assessment_results,
                "conversation_state": conversation['state'],
                "message_count": len(conversation['history'])
            }
            
        except Exception as e:
            logger.error(f"Voice processing error: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _process_native_conversation(
        self,
        text: str,
        language: str,
        conversation: Dict[str, Any]
    ) -> str:
        """
        Process conversation in user's native language using Gemini
        """
        try:
            # Get session ID for Gemini
            session_id = conversation['gemini_session_id']
            
            # Chat with Gemini (it will respond in same language)
            result = self.gemini.chat(session_id, text)
            
            if "error" in result:
                return "I apologize, I'm having trouble processing that. Could you please rephrase?"
            
            return result["message"]
            
        except Exception as e:
            logger.error(f"Native conversation error: {e}")
            return "I'm here to help. Please tell me about your health concerns."
    
    async def _extract_information(
        self,
        english_text: str,
        conversation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract structured information from English text
        """
        try:
            # Use Gemini's extraction from the session
            session_id = conversation['gemini_session_id']
            session_data = self.gemini.get_session(session_id)
            
            if session_data and 'extracted_info' in session_data:
                return session_data['extracted_info']
            
            return {
                "symptoms": [],
                "patient_info": {},
                "ready_for_assessment": False
            }
            
        except Exception as e:
            logger.error(f"Information extraction error: {e}")
            return {
                "symptoms": [],
                "patient_info": {},
                "ready_for_assessment": False
            }
    
    def _create_conversation(self, language: str) -> str:
        """Create new conversation"""
        conversation_id = str(uuid.uuid4())
        
        # Start Gemini session
        gemini_session = self.gemini.start_session(conversation_id, language)
        
        self.conversations[conversation_id] = {
            'id': conversation_id,
            'gemini_session_id': gemini_session['session_id'],
            'language': language,
            'history': [],
            'extracted_data': {
                'patient_info': {},
                'symptoms': [],
                'medical_history': []
            },
            'state': 'greeting',
            'created_at': datetime.now().isoformat()
        }
        
        logger.info(f"Created conversation {conversation_id} in language {language}")
        return conversation_id
    
    def _update_extracted_data(
        self,
        conversation: Dict[str, Any],
        extracted: Dict[str, Any]
    ):
        """Update conversation with extracted information"""
        # Merge patient info
        if extracted.get('patient_info'):
            conversation['extracted_data']['patient_info'].update(
                extracted['patient_info']
            )
        
        # Add new symptoms (avoid duplicates)
        if extracted.get('symptoms'):
            existing_symptoms = {
                s['name'].lower() for s in conversation['extracted_data']['symptoms']
            }
            
            for symptom in extracted['symptoms']:
                if symptom['name'].lower() not in existing_symptoms:
                    conversation['extracted_data']['symptoms'].append(symptom)
        
        # Update state
        if extracted.get('ready_for_assessment'):
            conversation['state'] = 'ready_for_assessment'
    
    async def _run_assessment(
        self,
        conversation: Dict[str, Any],
        language: str
    ) -> Dict[str, Any]:
        """
        Run complete assessment with extracted data
        """
        try:
            extracted_data = conversation['extracted_data']
            
            # Prepare symptoms for analysis
            symptoms = extracted_data.get('symptoms', [])
            if not symptoms:
                return None
            
            # Analyze symptoms
            symptom_result = symptom_analyzer.analyze_symptoms(
                symptoms=[s['name'] for s in symptoms],
                locale='en'
            )
            
            # Translate results back to user's language
            if language != 'en':
                translated_result = await self._translate_results(
                    symptom_result,
                    language
                )
                return translated_result
            
            return symptom_result
            
        except Exception as e:
            logger.error(f"Assessment error: {e}", exc_info=True)
            return None
    
    async def _translate_results(
        self,
        results: Dict[str, Any],
        target_language: str
    ) -> Dict[str, Any]:
        """Translate assessment results to user's language"""
        try:
            translated = results.copy()
            
            # Translate diagnosis explanation
            if 'diagnosis' in results and 'explanation' in results['diagnosis']:
                translated['diagnosis']['explanation'] = self.translator.from_english(
                    results['diagnosis']['explanation'],
                    target_language
                )
            
            # Translate recommendations
            if 'recommendations' in results:
                for category in ['dietary', 'lifestyle', 'herbal', 'yoga']:
                    if category in results['recommendations']:
                        translated['recommendations'][category] = [
                            self.translator.from_english(item, target_language)
                            for item in results['recommendations'][category]
                        ]
            
            return translated
            
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return results
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation data"""
        return self.conversations.get(conversation_id)
    
    def end_conversation(self, conversation_id: str):
        """End conversation"""
        if conversation_id in self.conversations:
            conversation = self.conversations[conversation_id]
            
            # End Gemini session
            self.gemini.end_session(conversation['gemini_session_id'])
            
            # Remove conversation
            del self.conversations[conversation_id]
            logger.info(f"Ended conversation {conversation_id}")
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        return [
            "en",  # English
            "hi",  # Hindi
            "ta",  # Tamil
            "te",  # Telugu
            "bn",  # Bengali
            "mr",  # Marathi
            "gu",  # Gujarati
            "kn",  # Kannada
            "ml",  # Malayalam
            "pa",  # Punjabi
            "or",  # Odia
        ]

# Global instance
multilingual_voice_service = MultilingualVoiceService()
