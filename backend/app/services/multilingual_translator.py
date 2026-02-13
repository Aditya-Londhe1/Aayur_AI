# backend/app/services/multilingual_translator.py
"""
Multilingual Translation Service
Handles translation between any language and English for backend processing
"""

import logging
from typing import Dict, Any, Optional
from deep_translator import GoogleTranslator
from langdetect import detect, detect_langs, LangDetectException
import json

logger = logging.getLogger(__name__)

class MultilingualTranslator:
    """
    Handle translation between any language and English
    """
    
    def __init__(self):
        self.cache = {}  # Cache translations to reduce API calls
        
        # Language code mapping
        self.language_map = {
            'hi': 'hi',  # Hindi
            'ta': 'ta',  # Tamil
            'te': 'te',  # Telugu
            'bn': 'bn',  # Bengali
            'mr': 'mr',  # Marathi
            'gu': 'gu',  # Gujarati
            'kn': 'kn',  # Kannada
            'ml': 'ml',  # Malayalam
            'pa': 'pa',  # Punjabi
            'or': 'or',  # Odia
            'en': 'en',  # English
        }
        
        # Symptom standardization map
        self.symptom_map = {
            # Headache variations
            "head pain": "Headache",
            "head ache": "Headache",
            "pain in head": "Headache",
            "sir dard": "Headache",
            "thala vali": "Headache",
            
            # Stomach variations
            "stomach pain": "Abdominal Pain",
            "belly pain": "Abdominal Pain",
            "tummy ache": "Abdominal Pain",
            "pet dard": "Abdominal Pain",
            "vayiru vali": "Abdominal Pain",
            
            # Fever variations
            "high temperature": "Fever",
            "bukhar": "Fever",
            "kaichal": "Fever",
            "jwaram": "Fever",
            
            # Fatigue variations
            "tiredness": "Fatigue",
            "weakness": "Fatigue",
            "thakan": "Fatigue",
            "alasata": "Fatigue",
            
            # Cold/Cough
            "running nose": "Cold",
            "sardi": "Cold",
            "khansi": "Cough",
            "irumal": "Cough",
            
            # Sleep issues
            "can't sleep": "Insomnia",
            "no sleep": "Insomnia",
            "neend nahi aati": "Insomnia",
            
            # Digestive issues
            "loose motion": "Diarrhea",
            "dast": "Diarrhea",
            "kabz": "Constipation",
            "gas": "Bloating",
            "acidity": "Acidity",
        }
    
    def detect_language(self, text: str) -> Dict[str, Any]:
        """
        Detect language from text
        
        Args:
            text: Input text in any language
            
        Returns:
            Dictionary with language code and confidence
        """
        try:
            detected = detect(text)
            probabilities = detect_langs(text)
            
            # Get confidence
            confidence = 0.0
            for prob in probabilities:
                if prob.lang == detected:
                    confidence = prob.prob
                    break
            
            return {
                "language": detected,
                "confidence": confidence,
                "all_probabilities": [
                    {"lang": p.lang, "prob": p.prob} 
                    for p in probabilities
                ]
            }
        except LangDetectException as e:
            logger.warning(f"Language detection failed: {e}")
            return {
                "language": "en",
                "confidence": 0.5,
                "error": str(e)
            }
    
    def to_english(self, text: str, source_lang: Optional[str] = None) -> str:
        """
        Translate any language to English for backend processing
        
        Args:
            text: Text in source language
            source_lang: Source language code (auto-detect if None)
            
        Returns:
            Translated English text
        """
        if not text or not text.strip():
            return ""
        
        # Check cache
        cache_key = f"{source_lang}:{text}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            # Auto-detect if not provided
            if not source_lang:
                lang_result = self.detect_language(text)
                source_lang = lang_result['language']
            
            # Skip translation if already English
            if source_lang == 'en':
                return text
            
            # Translate using deep-translator
            translator = GoogleTranslator(source=source_lang, target='en')
            translated = translator.translate(text)
            
            self.cache[cache_key] = translated
            
            logger.info(f"Translated '{text}' ({source_lang}) -> '{translated}' (en)")
            return translated
            
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return text  # Return original if translation fails
    
    def from_english(self, text: str, target_lang: str) -> str:
        """
        Translate English response back to user's language
        
        Args:
            text: English text
            target_lang: Target language code
            
        Returns:
            Translated text in target language
        """
        if not text or not text.strip():
            return ""
        
        # Skip if target is English
        if target_lang == 'en':
            return text
        
        # Check cache
        cache_key = f"en:{target_lang}:{text}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            translator = GoogleTranslator(source='en', target=target_lang)
            translated = translator.translate(text)
            
            self.cache[cache_key] = translated
            
            logger.info(f"Translated '{text}' (en) -> '{translated}' ({target_lang})")
            return translated
            
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return text
    
    def translate_symptoms(self, symptoms: list, source_lang: str) -> list:
        """
        Translate symptom list to English with medical term mapping
        
        Args:
            symptoms: List of symptom dictionaries
            source_lang: Source language code
            
        Returns:
            List of translated and standardized symptoms
        """
        translated_symptoms = []
        
        for symptom in symptoms:
            symptom_name = symptom.get('name', '')
            
            # Translate symptom name
            english_name = self.to_english(symptom_name, source_lang)
            
            # Standardize to medical term
            standardized = self._standardize_symptom(english_name)
            
            translated_symptoms.append({
                "name": standardized,
                "original_name": symptom_name,
                "original_language": source_lang,
                "severity": symptom.get('severity', 'moderate'),
                "duration": symptom.get('duration', '')
            })
        
        return translated_symptoms
    
    def _standardize_symptom(self, symptom_text: str) -> str:
        """
        Map colloquial terms to standard medical terms
        
        Args:
            symptom_text: Symptom description
            
        Returns:
            Standardized medical term
        """
        symptom_lower = symptom_text.lower().strip()
        
        # Check direct mapping
        if symptom_lower in self.symptom_map:
            return self.symptom_map[symptom_lower]
        
        # Check partial matches
        for key, value in self.symptom_map.items():
            if key in symptom_lower or symptom_lower in key:
                return value
        
        # Return title case if no mapping found
        return symptom_text.title()
    
    def clear_cache(self):
        """Clear translation cache"""
        self.cache = {}
        logger.info("Translation cache cleared")

# Global instance
multilingual_translator = MultilingualTranslator()
