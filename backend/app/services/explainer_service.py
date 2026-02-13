
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class ExplainerService:
    """
    Unified Explainable AI (XAI) Service.
    Generates human-readable explanations for AI decisions across all modalities.
    """
    
    def generate_comprehensive_explanation(self, consultation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a comprehensive explanation for the final diagnosis.
        """
        diagnosis = consultation.get("final_diagnosis", {})
        analyses = consultation.get("analyses", {})
        dominant_dosha = diagnosis.get("dominant_dosha")
        
        explanation = {
            "summary": self._generate_summary(diagnosis),
            "modalities": {}
        }
        
        # 1. Tongue Analysis Explanation (Grad-CAM)
        if "tongue" in analyses:
            tongue = analyses["tongue"]
            explanation["modalities"]["tongue"] = {
                "contribution": "Visual features (Color, Coating)",
                "details": tongue.get("explainability", {}).get("explanation_text", "No detailed explanation available."),
                "heatmap": tongue.get("explainability", {}).get("heatmap_image") # Base64
            }

        # 2. Pulse Analysis Explanation (Feature Attribution)
        if "pulse" in analyses:
            explanation["modalities"]["pulse"] = self._explain_pulse(analyses["pulse"], dominant_dosha)

        # 3. Symptom Analysis Explanation (Keyword contributions)
        if "symptoms" in analyses:
            explanation["modalities"]["symptoms"] = self._explain_symptoms(analyses["symptoms"], dominant_dosha)

        # 4. Voice Analysis
        if "voice" in analyses: # If we store it there (currently inside consultation_data but checking structure)
             pass # Logic for voice if added to main analyses dict

        return explanation

    def _generate_summary(self, diagnosis: Dict[str, Any]) -> str:
        dosha = diagnosis.get("dominant_dosha") or "balanced"
        level = diagnosis.get("imbalance_level") or "mild"
        dosha_name = dosha.capitalize() if dosha else "Balanced"
        return f"The system has identified a {level} {dosha_name} imbalance based on the weighted aggregation of multiple physiological markers."

    def _explain_pulse(self, pulse_result: Dict[str, Any], target_dosha: str) -> Dict[str, Any]:
        features = pulse_result.get("features", {})
        
        # Handle None or empty target_dosha
        if not target_dosha:
            target_dosha = "balanced"
        
        # Rule-based explanation of features
        reasons = []
        if target_dosha == "vata":
            if features.get("hrv", 0) > 50: reasons.append("High Heart Rate Variability (Irregularity)")
            if features.get("heart_rate", 0) > 80: reasons.append("Elevated Heart Rate")
        elif target_dosha == "pitta":
            if features.get("heart_rate", 0) > 75: reasons.append("Strong, Fast Pulse")
        elif target_dosha == "kapha":
            if features.get("heart_rate", 0) < 65: reasons.append("Slow, Steady Pulse")
            if features.get("hrv", 0) < 30: reasons.append("Low Heart Rate Variability (Stability)")
        
        dosha_name = target_dosha.capitalize() if target_dosha else "Balanced"
        return {
            "contribution": "Physiological Rhythms",
            "details": f"Pulse features supporting {dosha_name}: {', '.join(reasons) if reasons else 'General pulse characteristics match this profile.'}",
            "key_features": features
        }

    def _explain_symptoms(self, symptom_result: Dict[str, Any], target_dosha: str) -> Dict[str, Any]:
        # Handle None or empty target_dosha
        if not target_dosha:
            target_dosha = "balanced"
            
        # Identify top symptoms for this dosha
        symptoms = symptom_result.get("symptom_analysis", [])
        
        supporting_symptoms = [
            s["symptom"] for s in symptoms 
            if s.get("primary_dosha") == target_dosha
        ]
        
        text = "No specific symptoms reported."
        if supporting_symptoms:
            dosha_name = target_dosha.capitalize() if target_dosha else "Balanced"
            text = f"The following reported symptoms are strong indicators of {dosha_name}: {', '.join(supporting_symptoms[:3])}."
            
        return {
            "contribution": "Self-reported Conditions",
            "details": text,
            "supporting_symptoms": supporting_symptoms
        }

explainer_service = ExplainerService()
