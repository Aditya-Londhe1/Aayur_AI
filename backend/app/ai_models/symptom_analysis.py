
import torch
import logging
from typing import Dict, List, Any, Optional
import json
import re

# Try to import transformers, fallback to keyword analysis if not available
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    pipeline = None
    TRANSFORMERS_AVAILABLE = False

logger = logging.getLogger(__name__)

class SymptomAnalyzer:
    """
    Symptom Analysis using Zero-Shot Classification Transformer.
    Classifies symptom descriptions into Ayurvedic Dosha imbalances.
    Falls back to keyword-based analysis if transformers unavailable.
    """
    
    def __init__(self, model_name: str = "facebook/bart-large-mnli", device: int = -1):
        """
        Initialize the symptom analyzer.
        Args:
            model_name: Hugging Face model name for zero-shot classification.
            device: Device to run on (-1 for CPU, 0+ for GPU).
        """
        self.model_name = model_name
        self.device = 0 if torch.cuda.is_available() else -1
        self.classifier = None
        self.is_loaded = False
        
        self.labels = [
            "Vata imbalance (dryness, anxiety, cold, movement issues)",
            "Pitta imbalance (heat, inflammation, anger, digestion issues)",
            "Kapha imbalance (heaviness, congestion, lethargy, weight gain)",
            "Balanced health"
        ]
        
        # Enhanced keywords for heuristic fallback
        self.keywords = {
            "Vata": [
                "dry", "anxiety", "cold", "movement", "pain", "gas", "bloating", 
                "insomnia", "fear", "thin", "constipation", "restless", "worry",
                "irregular", "variable", "rough", "light", "mobile", "quick",
                "nervous", "tremor", "cracking", "joint pain", "stiff"
            ],
            "Pitta": [
                "heat", "inflammation", "anger", "fire", "acid", "sweat", "red", 
                "burning", "irritability", "sharp", "hot", "fever", "rash",
                "acidity", "heartburn", "ulcer", "impatient", "critical",
                "perfectionist", "competitive", "intense", "yellow", "oily"
            ],
            "Kapha": [
                "heavy", "congestion", "lethargy", "weight", "cold", "mucus", 
                "sleep", "swelling", "slow", "attachment", "dull", "thick",
                "sticky", "sweet", "stable", "calm", "patient", "loving",
                "possessive", "greedy", "lazy", "overweight", "phlegm"
            ]
        }
        
        # Symptom severity mapping
        self.severity_keywords = {
            "mild": ["slight", "little", "minor", "occasional"],
            "moderate": ["moderate", "regular", "frequent", "noticeable"],
            "severe": ["severe", "intense", "extreme", "constant", "unbearable"]
        }
        
        logger.info(f"SymptomAnalyzer initialized. Transformers available: {TRANSFORMERS_AVAILABLE}")

    def load_model(self):
        """Lazy load the model pipeline with proper error handling"""
        if self.is_loaded:
            return True
            
        if not TRANSFORMERS_AVAILABLE:
            logger.warning("Transformers library not available. Using keyword-based analysis only.")
            self.is_loaded = True
            return False

        try:
            logger.info(f"Loading Symptom Analysis model: {self.model_name}")
            self.classifier = pipeline(
                "zero-shot-classification",
                model=self.model_name,
                device=self.device,
                return_all_scores=True
            )
            self.is_loaded = True
            logger.info("Symptom Analysis model loaded successfully.")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load Symptom Analysis model: {e}")
            logger.warning("Falling back to keyword-based analysis")
            self.classifier = None
            self.is_loaded = True
            return False

    def analyze(self, symptoms: List[Dict], patient_info: Dict = None) -> Dict[str, Any]:
        """
        Analyze symptoms and return dosha analysis
        
        Args:
            symptoms: List of symptom dictionaries with 'name', 'severity', 'duration'
                     OR list of symptom strings (will be normalized)
            patient_info: Additional patient information
            
        Returns:
            Dictionary with dosha analysis results
        """
        try:
            # Ensure model is loaded
            if not self.is_loaded:
                self.load_model()
            
            # Normalize symptoms to dict format if they're strings
            symptoms = self._normalize_symptoms(symptoms)
            
            # Prepare symptom text
            symptom_text = self._prepare_symptom_text(symptoms)
            
            if not symptom_text.strip():
                return self._get_default_analysis()
            
            # Try transformer analysis first
            if self.classifier is not None:
                try:
                    return self._transformer_analysis(symptom_text, symptoms, patient_info)
                except Exception as e:
                    logger.warning(f"Transformer analysis failed: {e}. Using keyword fallback.")
            
            # Fallback to keyword analysis
            return self._heuristic_analysis(symptom_text, symptoms, patient_info)
            
        except Exception as e:
            logger.error(f"Symptom analysis error: {e}")
            return self._get_error_analysis(str(e))
    
    def _normalize_symptoms(self, symptoms: List) -> List[Dict]:
        """Normalize symptoms to dict format"""
        normalized = []
        for symptom in symptoms:
            if isinstance(symptom, str):
                # Convert string to dict
                normalized.append({
                    "name": symptom,
                    "severity": "moderate",
                    "duration": "",
                    "description": ""
                })
            elif isinstance(symptom, dict):
                # Ensure all required keys exist
                normalized.append({
                    "name": symptom.get("name", ""),
                    "severity": symptom.get("severity", "moderate"),
                    "duration": symptom.get("duration", ""),
                    "description": symptom.get("description", "")
                })
            else:
                logger.warning(f"Invalid symptom format: {symptom}")
        return normalized

    def _prepare_symptom_text(self, symptoms: List[Dict]) -> str:
        """Prepare symptom text for analysis"""
        if not symptoms:
            return ""
        
        symptom_descriptions = []
        for symptom in symptoms:
            name = symptom.get("name", "")
            severity = symptom.get("severity", "")
            duration = symptom.get("duration", "")
            description = symptom.get("description", "")
            
            # Build symptom description
            parts = [name]
            if severity:
                parts.append(f"severity: {severity}")
            if duration:
                parts.append(f"duration: {duration}")
            if description:
                parts.append(description)
            
            symptom_descriptions.append(" ".join(parts))
        
        return ". ".join(symptom_descriptions)

    def _transformer_analysis(self, symptom_text: str, symptoms: List[Dict], patient_info: Dict) -> Dict[str, Any]:
        """Perform transformer-based analysis"""
        try:
            # Run zero-shot classification
            result = self.classifier(symptom_text, self.labels)
            
            # Process results
            dosha_scores = {}
            for label, score in zip(result['labels'], result['scores']):
                if "Vata" in label:
                    dosha_scores["vata"] = float(score)
                elif "Pitta" in label:
                    dosha_scores["pitta"] = float(score)
                elif "Kapha" in label:
                    dosha_scores["kapha"] = float(score)
                elif "Balanced" in label:
                    dosha_scores["balanced"] = float(score)
            
            # Normalize dosha scores (exclude balanced)
            total_dosha = sum(dosha_scores.get(d, 0) for d in ["vata", "pitta", "kapha"])
            if total_dosha > 0:
                for dosha in ["vata", "pitta", "kapha"]:
                    if dosha in dosha_scores:
                        dosha_scores[dosha] = dosha_scores[dosha] / total_dosha
            
            # Determine dominant dosha
            dominant_dosha = max(dosha_scores, key=dosha_scores.get)
            confidence = dosha_scores[dominant_dosha]
            
            # Analyze individual symptoms
            symptom_analysis = self._analyze_individual_symptoms(symptoms)
            
            return {
                "dominant_dosha": dominant_dosha,
                "confidence": confidence,
                "dosha_contributions": dosha_scores,
                "symptom_analysis": symptom_analysis,
                "overall_severity": self._calculate_overall_severity(symptoms),
                "likely_conditions": self._identify_likely_conditions(symptoms, dominant_dosha),
                "original_text": symptom_text,
                "method": "transformer_zero_shot",
                "model_used": self.model_name
            }
            
        except Exception as e:
            logger.error(f"Transformer analysis failed: {e}")
            raise

    def _heuristic_analysis(self, symptom_text: str, symptoms: List[Dict], patient_info: Dict) -> Dict[str, Any]:
        """Enhanced keyword-based analysis when transformers unavailable"""
        text_lower = symptom_text.lower()
        scores = {"vata": 0.0, "pitta": 0.0, "kapha": 0.0}
        
        # Count keyword matches with weights
        total_weight = 0
        for dosha, keywords in self.keywords.items():
            dosha_key = dosha.lower()
            weight = 0
            
            for keyword in keywords:
                if keyword in text_lower:
                    # Weight based on keyword importance and frequency
                    frequency = text_lower.count(keyword)
                    importance = 1.0
                    
                    # Higher weight for primary symptoms
                    if keyword in ["pain", "inflammation", "congestion", "anxiety", "lethargy"]:
                        importance = 2.0
                    
                    weight += frequency * importance
            
            scores[dosha_key] = weight
            total_weight += weight
        
        # Normalize scores
        if total_weight > 0:
            for dosha in scores:
                scores[dosha] = scores[dosha] / total_weight
        else:
            # Default to balanced if no keywords found
            scores = {"vata": 0.33, "pitta": 0.33, "kapha": 0.33}
        
        # Determine dominant dosha
        dominant_dosha = max(scores, key=scores.get)
        confidence = scores[dominant_dosha]
        
        # Analyze individual symptoms
        symptom_analysis = self._analyze_individual_symptoms(symptoms)
        
        return {
            "dominant_dosha": dominant_dosha,
            "confidence": confidence,
            "dosha_contributions": scores,
            "symptom_analysis": symptom_analysis,
            "overall_severity": self._calculate_overall_severity(symptoms),
            "likely_conditions": self._identify_likely_conditions(symptoms, dominant_dosha),
            "original_text": symptom_text,
            "method": "heuristic_keyword_match",
            "keyword_matches": self._get_keyword_matches(text_lower)
        }

    def _analyze_individual_symptoms(self, symptoms: List[Dict]) -> List[Dict]:
        """Analyze each symptom individually"""
        analysis = []
        
        for symptom in symptoms:
            name = symptom.get("name", "").lower()
            severity = symptom.get("severity", "mild").lower()
            
            # Determine dosha association for this symptom
            dosha_scores = {"vata": 0, "pitta": 0, "kapha": 0}
            
            for dosha, keywords in self.keywords.items():
                dosha_key = dosha.lower()
                for keyword in keywords:
                    if keyword in name:
                        dosha_scores[dosha_key] += 1
            
            # Determine primary dosha for this symptom
            if sum(dosha_scores.values()) > 0:
                primary_dosha = max(dosha_scores, key=dosha_scores.get)
            else:
                primary_dosha = "unknown"
            
            # Map severity
            severity_score = {
                "mild": 0.3,
                "moderate": 0.6,
                "severe": 0.9
            }.get(severity, 0.5)
            
            analysis.append({
                "symptom": symptom.get("name", ""),
                "primary_dosha": primary_dosha,
                "severity_score": severity_score,
                "dosha_scores": dosha_scores
            })
        
        return analysis

    def _calculate_overall_severity(self, symptoms: List[Dict]) -> str:
        """Calculate overall severity of symptoms"""
        if not symptoms:
            return "none"
        
        severity_scores = []
        for symptom in symptoms:
            severity = symptom.get("severity", "mild").lower()
            score = {
                "mild": 1,
                "moderate": 2,
                "severe": 3
            }.get(severity, 1)
            severity_scores.append(score)
        
        avg_severity = sum(severity_scores) / len(severity_scores)
        
        if avg_severity >= 2.5:
            return "severe"
        elif avg_severity >= 1.5:
            return "moderate"
        else:
            return "mild"

    def _identify_likely_conditions(self, symptoms: List[Dict], dominant_dosha: str) -> List[Dict]:
        """Identify likely conditions based on symptoms and dosha"""
        conditions = []
        
        symptom_names = [s.get("name", "").lower() for s in symptoms]
        symptom_text = " ".join(symptom_names)
        
        # Common condition patterns
        condition_patterns = {
            "Digestive Issues": ["stomach", "digestion", "acid", "bloating", "gas", "constipation"],
            "Stress and Anxiety": ["stress", "anxiety", "worry", "nervous", "restless"],
            "Sleep Disorders": ["sleep", "insomnia", "tired", "fatigue", "lethargy"],
            "Respiratory Issues": ["cough", "cold", "congestion", "breathing", "phlegm"],
            "Joint and Muscle Pain": ["joint", "muscle", "pain", "stiff", "ache"],
            "Skin Issues": ["skin", "rash", "dry", "oily", "acne", "eczema"],
            "Headaches": ["headache", "migraine", "head", "pressure"],
            "Weight Issues": ["weight", "heavy", "overweight", "thin", "appetite"]
        }
        
        for condition, keywords in condition_patterns.items():
            matches = sum(1 for keyword in keywords if keyword in symptom_text)
            if matches > 0:
                confidence = min(matches / len(keywords), 1.0)
                conditions.append({
                    "name": condition,
                    "confidence": confidence,
                    "associated_dosha": dominant_dosha,
                    "keyword_matches": matches
                })
        
        # Sort by confidence and return top 5
        conditions.sort(key=lambda x: x["confidence"], reverse=True)
        return conditions[:5]

    def _get_keyword_matches(self, text_lower: str) -> Dict[str, List[str]]:
        """Get matched keywords for each dosha"""
        matches = {}
        for dosha, keywords in self.keywords.items():
            dosha_matches = [kw for kw in keywords if kw in text_lower]
            if dosha_matches:
                matches[dosha.lower()] = dosha_matches
        return matches

    def _get_default_analysis(self) -> Dict[str, Any]:
        """Return default analysis when no symptoms provided"""
        return {
            "dominant_dosha": "balanced",
            "confidence": 0.5,
            "dosha_contributions": {"vata": 0.33, "pitta": 0.33, "kapha": 0.33},
            "symptom_analysis": [],
            "overall_severity": "none",
            "likely_conditions": [],
            "original_text": "",
            "method": "default_no_symptoms"
        }

    def _get_error_analysis(self, error_msg: str) -> Dict[str, Any]:
        """Return error analysis"""
        return {
            "dominant_dosha": "unknown",
            "confidence": 0.0,
            "dosha_contributions": {"vata": 0.0, "pitta": 0.0, "kapha": 0.0},
            "symptom_analysis": [],
            "overall_severity": "unknown",
            "likely_conditions": [],
            "original_text": "",
            "method": "error",
            "error": error_msg
        }

# Global instance
symptom_analyzer = SymptomAnalyzer()
