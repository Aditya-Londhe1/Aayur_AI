# voice_services/speech_recognition/stt_service.py
import os
import asyncio
from typing import Dict, Any, Optional
import speech_recognition as sr
from google.cloud import speech_v1
import azure.cognitiveservices.speech as speechsdk
import vosk
import json

class SpeechToTextService:
    """Multi-engine speech recognition service"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Initialize different STT engines
        self.recognizer = sr.Recognizer()
        
        # Google Cloud Speech-to-Text
        self.google_client = None
        if config.get('GOOGLE_APPLICATION_CREDENTIALS'):
            self.google_client = speech_v1.SpeechClient()
        
        # Azure Speech Services
        self.azure_config = None
        if config.get('AZURE_SPEECH_KEY'):
            self.azure_config = speechsdk.SpeechConfig(
                subscription=config['AZURE_SPEECH_KEY'],
                region=config.get('AZURE_SPEECH_REGION', 'eastus')
            )
        
        # Vosk (offline) models
        self.vosk_models = {}
        self._load_vosk_models()
        
        # Language mappings
        self.language_codes = {
            'en': 'en-US',
            'hi': 'hi-IN',
            'ta': 'ta-IN',
            'te': 'te-IN',
            'kn': 'kn-IN',
            'ml': 'ml-IN',
            'bn': 'bn-IN',
            'gu': 'gu-IN',
            'mr': 'mr-IN',
            'pa': 'pa-IN',
            'ur': 'ur-PK'
        }
    
    def _load_vosk_models(self):
        """Load Vosk models for offline recognition"""
        model_dir = self.config.get('VOSK_MODEL_DIR', 'voice_services/models/vosk_models/')
        if os.path.exists(model_dir):
            for lang in ['en', 'hi', 'ta', 'te']:
                lang_dir = os.path.join(model_dir, lang)
                if os.path.exists(lang_dir):
                    try:
                        self.vosk_models[lang] = vosk.Model(lang_dir)
                    except:
                        pass
    
    async def recognize(self, audio_data: bytes, 
                       language: str = 'en',
                       context: str = 'general') -> Dict[str, Any]:
        """
        Recognize speech using best available engine
        
        Priority:
        1. Google Cloud STT (best accuracy)
        2. Azure Speech Services (Indian languages)
        3. Vosk (offline fallback)
        4. SpeechRecognition library (last resort)
        """
        try:
            # Try Google Cloud first
            if self.google_client and language in ['en', 'hi']:
                return await self._recognize_google(audio_data, language, context)
            
            # Try Azure for Indian languages
            elif self.azure_config and language in self.language_codes:
                return await self._recognize_azure(audio_data, language, context)
            
            # Try Vosk offline
            elif language in self.vosk_models:
                return await self._recognize_vosk(audio_data, language)
            
            # Fallback to SpeechRecognition
            else:
                return await self._recognize_sr(audio_data, language)
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'confidence': 0.0
            }
    
    async def _recognize_google(self, audio_data: bytes, 
                              language: str, 
                              context: str) -> Dict[str, Any]:
        """Use Google Cloud Speech-to-Text"""
        # Configure for medical context
        if context == 'medical_symptoms':
            phrases = [
                "headache", "fever", "cough", "pain", "fatigue",
                "insomnia", "anxiety", "constipation", "heartburn"
            ]
            speech_contexts = [speech_v1.SpeechContext(phrases=phrases)]
        else:
            speech_contexts = []
        
        # Configure audio
        audio = speech_v1.RecognitionAudio(content=audio_data)
        config = speech_v1.RecognitionConfig(
            encoding=speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code=self.language_codes.get(language, 'en-US'),
            speech_contexts=speech_contexts,
            enable_automatic_punctuation=True,
            model='medical_dictation' if context == 'medical' else 'default'
        )
        
        # Send request
        response = self.google_client.recognize(config=config, audio=audio)
        
        if response.results:
            result = response.results[0]
            return {
                'success': True,
                'text': result.alternatives[0].transcript,
                'confidence': result.alternatives[0].confidence,
                'alternatives': [
                    alt.transcript for alt in result.alternatives[1:]
                ] if len(result.alternatives) > 1 else []
            }
        
        return {
            'success': False,
            'text': '',
            'confidence': 0.0
        }
    
    async def _recognize_azure(self, audio_data: bytes, 
                             language: str, 
                             context: str) -> Dict[str, Any]:
        """Use Azure Speech Services"""
        audio_config = speechsdk.audio.AudioConfig(filename=None)
        audio_stream = speechsdk.audio.PushAudioInputStream()
        
        # Write audio data to stream
        audio_stream.write(audio_data)
        audio_stream.close()
        
        # Configure recognizer
        self.azure_config.speech_recognition_language = self.language_codes[language]
        
        if context == 'medical_symptoms':
            # Enable medical phrase list
            phrase_list_grammar = speechsdk.PhraseListGrammar.from_recognizer(
                speechsdk.SpeechRecognizer(
                    speech_config=self.azure_config,
                    audio_config=audio_config
                )
            )
            phrase_list_grammar.addPhrase("headache")
            phrase_list_grammar.addPhrase("fever")
            # Add more medical phrases
        
        recognizer = speechsdk.SpeechRecognizer(
            speech_config=self.azure_config,
            audio_config=audio_config
        )
        
        # Perform recognition
        result = recognizer.recognize_once()
        
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            return {
                'success': True,
                'text': result.text,
                'confidence': 1.0,  # Azure doesn't provide confidence score
                'alternatives': []
            }
        
        return {
            'success': False,
            'text': '',
            'confidence': 0.0
        }
    
    async def detect_language(self, audio_data: bytes) -> Optional[str]:
        """Auto-detect language from audio"""
        # Try to detect using audio characteristics
        # For simplicity, return None (let user choose)
        return None