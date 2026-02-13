# voice_services/text_to_speech/tts_service.py
import os
import asyncio
from typing import Dict, Any, Optional
from gtts import gTTS
import boto3
from io import BytesIO
import tempfile

class TextToSpeechService:
    """Multi-engine text-to-speech service"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Amazon Polly client (for Indian languages)
        self.polly_client = None
        if config.get('AWS_ACCESS_KEY_ID') and config.get('AWS_SECRET_ACCESS_KEY'):
            self.polly_client = boto3.client(
                'polly',
                aws_access_key_id=config['AWS_ACCESS_KEY_ID'],
                aws_secret_access_key=config['AWS_SECRET_ACCESS_KEY'],
                region_name=config.get('AWS_REGION', 'ap-south-1')
            )
        
        # Voice profiles for different contexts
        self.voice_profiles = {
            'friendly': {
                'rate': 'medium',
                'pitch': 'medium',
                'volume': 'medium'
            },
            'professional': {
                'rate': 'slow',
                'pitch': 'low',
                'volume': 'medium'
            },
            'soothing': {
                'rate': 'slow',
                'pitch': 'low',
                'volume': 'soft'
            },
            'authoritative': {
                'rate': 'medium',
                'pitch': 'low',
                'volume': 'loud'
            },
            'calm': {
                'rate': 'slow',
                'pitch': 'medium',
                'volume': 'soft'
            },
            'clear': {
                'rate': 'medium',
                'pitch': 'medium',
                'volume': 'medium'
            }
        }
        
        # Language to voice mapping for Polly
        self.language_voices = {
            'en': {'voice_id': 'Joanna', 'engine': 'neural'},
            'hi': {'voice_id': 'Aditi', 'engine': 'standard'},
            'ta': {'voice_id': 'Kajal', 'engine': 'standard'},
            'te': {'voice_id': 'Kajal', 'engine': 'standard'},
            'kn': {'voice_id': 'Kajal', 'engine': 'standard'},
            'ml': {'voice_id': 'Kajal', 'engine': 'standard'},
            'bn': {'voice_id': 'Kajal', 'engine': 'standard'},
            'gu': {'voice_id': 'Kajal', 'engine': 'standard'},
            'mr': {'voice_id': 'Kajal', 'engine': 'standard'},
            'pa': {'voice_id': 'Kajal', 'engine': 'standard'},
            'ur': {'voice_id': 'Kajal', 'engine': 'standard'}
        }
    
    async def synthesize(self, text: str, 
                        language: str = 'en',
                        voice_type: str = 'friendly',
                        speed: float = 1.0) -> Dict[str, Any]:
        """
        Convert text to speech
        
        Priority:
        1. Amazon Polly (for Indian languages and high quality)
        2. Google TTS (free, good for English)
        3. Offline TTS (fallback)
        """
        try:
            # Use Polly for Indian languages
            if language != 'en' and self.polly_client:
                return await self._synthesize_polly(text, language, voice_type, speed)
            
            # Use Polly for English if available
            elif self.polly_client:
                return await self._synthesize_polly(text, language, voice_type, speed)
            
            # Fallback to Google TTS
            else:
                return await self._synthesize_gtts(text, language, speed)
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'audio_data': None,
                'format': None
            }
    
    async def _synthesize_polly(self, text: str, 
                              language: str, 
                              voice_type: str,
                              speed: float) -> Dict[str, Any]:
        """Use Amazon Polly for high-quality speech"""
        voice_config = self.language_voices.get(language, self.language_voices['en'])
        
        # Apply voice profile
        profile = self.voice_profiles.get(voice_type, self.voice_profiles['friendly'])
        
        # SSML for better speech control
        ssml_text = f"""
        <speak>
            <prosody rate="{speed}" pitch="{profile['pitch']}" volume="{profile['volume']}">
                {text}
            </prosody>
        </speak>
        """
        
        # Request synthesis
        response = self.polly_client.synthesize_speech(
            Text=ssml_text,
            TextType='ssml',
            OutputFormat='mp3',
            VoiceId=voice_config['voice_id'],
            Engine=voice_config['engine']
        )
        
        # Read audio stream
        audio_stream = response['AudioStream'].read()
        
        return {
            'success': True,
            'audio_data': audio_stream,
            'format': 'mp3',
            'duration': len(audio_stream) / 16000  # Approximate duration
        }
    
    async def _synthesize_gtts(self, text: str, 
                             language: str, 
                             speed: float) -> Dict[str, Any]:
        """Use Google Text-to-Speech (free)"""
        # Adjust speed (Google TTS has limited speed control)
        if speed < 0.8:
            # Add pauses for slower speech
            text = text.replace('.', '. ')
            text = text.replace(',', ', ')
        
        # Create TTS object
        tts = gTTS(
            text=text,
            lang=language,
            slow=(speed < 0.8)
        )
        
        # Save to bytes buffer
        buffer = BytesIO()
        tts.write_to_fp(buffer)
        buffer.seek(0)
        
        return {
            'success': True,
            'audio_data': buffer.read(),
            'format': 'mp3',
            'duration': len(text) / 15  # Approximate: 15 chars per second
        }