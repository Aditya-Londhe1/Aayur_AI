# backend/app/services/consultation_service.py
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import uuid

from app.services.ai_service import ai_service
from app.services.fusion_service import FusionService
from app.services.explainer_service import explainer_service
from app.i18n import t
from app.services import consultation_store

logger = logging.getLogger(__name__)

class ConsultationService:
    """
    Service for managing complete Ayurvedic consultations.
    Integrates multiple analysis types and generates comprehensive reports.
    """
    
    def __init__(self):
        self.ai_service = ai_service
        self.fusion_service = FusionService()
        self.explainer = explainer_service
        # Use global store instead of instance variable
        logger.info("ConsultationService initialized")
    
    async def create_consultation(self, patient_data: Dict[str, Any], locale: str = "en") -> Dict[str, Any]:
        """
        Create a new consultation session
        
        Args:
            patient_data: Patient information and preferences
            locale: Language locale for responses
            
        Returns:
            Consultation session data
        """
        try:
            consultation_id = f"CONS-{uuid.uuid4().hex[:8].upper()}"
            
            consultation = {
                "consultation_id": consultation_id,
                "patient_info": patient_data,
                "locale": locale,
                "status": "active",
                "created_at": datetime.now().isoformat(),
                "analyses": {},
                "final_diagnosis": None,
                "recommendations": None,
                "confidence_score": 0.0
            }
            
            # Store consultation in global store
            consultation_store.store_consultation(consultation_id, consultation)
            
            logger.info(f"Created consultation {consultation_id}")
            return consultation
            
        except Exception as e:
            logger.error(f"Failed to create consultation: {e}")
            raise
    
    async def get_consultation(self, consultation_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve consultation by ID"""
        return consultation_store.get_consultation(consultation_id)
    
    async def update_consultation(self, consultation: Dict[str, Any]) -> Dict[str, Any]:
        """Update consultation data"""
        consultation_id = consultation["consultation_id"]
        consultation["updated_at"] = datetime.now().isoformat()
        return consultation_store.update_consultation(consultation_id, consultation)
    
    async def add_tongue_analysis(self, consultation: Dict[str, Any], 
                                 image_path: str) -> Dict[str, Any]:
        """Add tongue analysis to consultation"""
        try:
            result = await self.ai_service.analyze_tongue(image_path, consultation["locale"])
            
            if result["success"]:
                consultation["analyses"]["tongue"] = result["analysis"]
                consultation = await self.update_consultation(consultation)
                logger.info(f"Added tongue analysis to {consultation['consultation_id']}")
            else:
                logger.warning(f"Tongue analysis failed: {result.get('error')}")
            
            return consultation
            
        except Exception as e:
            logger.error(f"Failed to add tongue analysis: {e}")
            raise
    
    async def add_pulse_analysis(self, consultation: Dict[str, Any], 
                                pulse_data: List[float]) -> Dict[str, Any]:
        """Add pulse analysis to consultation"""
        try:
            result = await self.ai_service.analyze_pulse(pulse_data, consultation["locale"])
            
            if result["success"]:
                consultation["analyses"]["pulse"] = result["analysis"]
                consultation = await self.update_consultation(consultation)
                logger.info(f"Added pulse analysis to {consultation['consultation_id']}")
            else:
                logger.warning(f"Pulse analysis failed: {result.get('error')}")
            
            return consultation
            
        except Exception as e:
            logger.error(f"Failed to add pulse analysis: {e}")
            raise
    
    async def add_symptom_analysis(self, consultation: Dict[str, Any], 
                                  symptoms: List[Dict]) -> Dict[str, Any]:
        """Add symptom analysis to consultation"""
        try:
            result = await self.ai_service.analyze_symptoms(
                symptoms, consultation["patient_info"], consultation["locale"]
            )
            
            if result["success"]:
                consultation["analyses"]["symptoms"] = result["analysis"]
                consultation = await self.update_consultation(consultation)
                logger.info(f"Added symptom analysis to {consultation['consultation_id']}")
            else:
                logger.warning(f"Symptom analysis failed: {result.get('error')}")
            
            return consultation
            
        except Exception as e:
            logger.error(f"Failed to add symptom analysis: {e}")
            raise
    
    async def finalize_consultation(self, consultation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Finalize consultation with integrated diagnosis and recommendations
        """
        try:
            if not consultation["analyses"]:
                raise ValueError("No analyses available for consultation")
            
            # Perform integrated analysis
            integrated_result = await self._integrate_analyses(consultation)
            
            # Update consultation with structured data
            consultation["final_diagnosis"] = integrated_result["diagnosis"]
            consultation["recommendations"] = integrated_result["recommendations"]
            consultation["confidence_score"] = integrated_result["confidence"]
            
            # Add structured format for frontend compatibility
            consultation["diagnosis"] = integrated_result["diagnosis"]
            consultation["confidence"] = integrated_result["confidence"]
            
            # Generate Comprehensive Explainability Report
            consultation["explanation"] = self.explainer.generate_comprehensive_explanation(consultation)
            
            consultation["status"] = "completed"
            consultation["completed_at"] = datetime.now().isoformat()
            
            logger.info(f"Finalized consultation {consultation['consultation_id']}")
            return consultation
            
        except Exception as e:
            logger.error(f"Failed to finalize consultation: {e}")
            raise
    
    async def _integrate_analyses(self, consultation: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate multiple analyses into final diagnosis"""
        try:
            analyses = consultation["analyses"]
            patient_data = consultation["patient_info"]
            locale = consultation["locale"]
            
            # Define weights based on available analyses
            weights = {}
            if "tongue" in analyses:
                weights["tongue"] = 0.4
            if "pulse" in analyses:
                weights["pulse"] = 0.3
            if "symptoms" in analyses:
                weights["symptoms"] = 0.3
            
            # Normalize weights
            total_weight = sum(weights.values())
            if total_weight > 0:
                weights = {k: v/total_weight for k, v in weights.items()}
            
            # Use fusion service for integration
            integrated_scores = self.fusion_service.fuse_dosha_scores(analyses, weights)
            
            # Determine final diagnosis
            dominant_dosha = max(integrated_scores, key=integrated_scores.get)
            dominant_score = integrated_scores[dominant_dosha]
            
            # Determine imbalance level
            if dominant_score > 0.6:
                imbalance = "severe"
            elif dominant_score > 0.45:
                imbalance = "moderate"
            else:
                imbalance = "mild"
            
            # Generate diagnosis
            diagnosis = {
                "dosha_scores": integrated_scores,
                "dominant_dosha": dominant_dosha,
                "imbalance_level": imbalance,
                "prakriti_type": self._determine_prakriti(integrated_scores),
                "vikriti_type": f"{dominant_dosha.capitalize()} imbalance",
                "explanation": self._generate_explanation(
                    integrated_scores, dominant_dosha, imbalance, locale
                )
            }
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                diagnosis, patient_data, analyses, locale
            )
            
            # Calculate confidence
            confidence = self._calculate_confidence(analyses, weights)
            
            return {
                "diagnosis": diagnosis,
                "recommendations": recommendations,
                "confidence": confidence
            }
            
        except Exception as e:
            logger.error(f"Failed to integrate analyses: {e}")
            raise
    
    async def _generate_recommendations(self, diagnosis: Dict[str, Any], 
                                       patient_data: Dict[str, Any],
                                       analyses: Dict[str, Any],
                                       locale: str) -> Dict[str, Any]:
        """Generate comprehensive recommendations"""
        dominant_dosha = diagnosis["dominant_dosha"]
        imbalance = diagnosis["imbalance_level"]
        
        # Base recommendations
        recommendations = self._get_base_recommendations(dominant_dosha, imbalance)
        
        # Add specific recommendations based on analyses
        if "symptoms" in analyses:
            symptom_recs = self._get_symptom_recommendations(analyses["symptoms"])
            self._merge_recommendations(recommendations, symptom_recs)
        
        if "tongue" in analyses:
            tongue_recs = self._get_tongue_recommendations(analyses["tongue"])
            self._merge_recommendations(recommendations, tongue_recs)
        
        if "pulse" in analyses:
            pulse_recs = self._get_pulse_recommendations(analyses["pulse"])
            self._merge_recommendations(recommendations, pulse_recs)
        
        # Add lifestyle recommendations based on patient info
        age = patient_data.get("age", 30)
        lifestyle_recs = self._get_age_specific_recommendations(age, dominant_dosha)
        self._merge_recommendations(recommendations, lifestyle_recs)
        
        # Add precautions and disclaimers
        recommendations["precautions"] = self._get_precautions(imbalance, locale)
        recommendations["disclaimer"] = self._get_disclaimer(locale)
        
        return recommendations
    
    def _get_base_recommendations(self, dominant_dosha: str, imbalance: str) -> Dict[str, List[str]]:
        """Get base recommendations for dosha imbalance"""
        base_recs = {
            "vata": {
                "dietary": [
                    "Eat warm, cooked foods",
                    "Include healthy fats like ghee",
                    "Avoid cold, raw foods",
                    "Eat at regular times"
                ],
                "lifestyle": [
                    "Maintain regular sleep schedule",
                    "Practice gentle exercises",
                    "Keep warm",
                    "Establish routines"
                ],
                "herbal": [
                    "Ashwagandha for stress",
                    "Brahmi for mental clarity",
                    "Triphala for digestion"
                ]
            },
            "pitta": {
                "dietary": [
                    "Eat cooling foods",
                    "Avoid spicy, hot foods",
                    "Include sweet, bitter tastes",
                    "Drink cool water"
                ],
                "lifestyle": [
                    "Avoid excessive heat",
                    "Practice cooling exercises",
                    "Maintain work-life balance",
                    "Take regular breaks"
                ],
                "herbal": [
                    "Aloe vera for cooling",
                    "Neem for purification",
                    "Coriander for digestion"
                ]
            },
            "kapha": {
                "dietary": [
                    "Eat light, warm foods",
                    "Avoid heavy, oily foods",
                    "Include spicy tastes",
                    "Reduce dairy intake"
                ],
                "lifestyle": [
                    "Engage in vigorous exercise",
                    "Wake up early",
                    "Stay active",
                    "Avoid daytime napping"
                ],
                "herbal": [
                    "Ginger for digestion",
                    "Turmeric for inflammation",
                    "Trikatu for metabolism"
                ]
            }
        }
        
        return base_recs.get(dominant_dosha, base_recs["vata"])
    
    def _get_symptom_recommendations(self, symptom_analysis: Dict[str, Any]) -> Dict[str, List[str]]:
        """Get recommendations based on symptom analysis"""
        recommendations = {"dietary": [], "lifestyle": [], "herbal": []}
        
        likely_conditions = symptom_analysis.get("likely_conditions", [])
        for condition in likely_conditions:
            condition_name = condition.get("name", "").lower()
            
            if "digestive" in condition_name:
                recommendations["dietary"].append("Eat easily digestible foods")
                recommendations["herbal"].append("Ginger tea for digestion")
            elif "stress" in condition_name:
                recommendations["lifestyle"].append("Practice stress management")
                recommendations["herbal"].append("Ashwagandha for stress relief")
            elif "sleep" in condition_name:
                recommendations["lifestyle"].append("Maintain sleep hygiene")
                recommendations["herbal"].append("Chamomile tea before bed")
        
        return recommendations
    
    def _get_tongue_recommendations(self, tongue_analysis: Dict[str, Any]) -> Dict[str, List[str]]:
        """Get recommendations based on tongue analysis"""
        recommendations = {"dietary": [], "lifestyle": [], "herbal": []}
        
        features = tongue_analysis.get("detailed_features", {})
        
        if features.get("coating", {}).get("type") == "thick_white":
            recommendations["dietary"].append("Reduce dairy and cold foods")
            recommendations["herbal"].append("Ginger for clearing mucus")
        
        if features.get("cracks", {}).get("present"):
            recommendations["dietary"].append("Increase hydration")
            recommendations["lifestyle"].append("Practice stress reduction")
        
        return recommendations
    
    def _get_pulse_recommendations(self, pulse_analysis: Dict[str, Any]) -> Dict[str, List[str]]:
        """Get recommendations based on pulse analysis"""
        recommendations = {"dietary": [], "lifestyle": [], "herbal": []}
        
        pulse_type = pulse_analysis.get("pulse_type", "")
        
        if "irregular" in pulse_type.lower():
            recommendations["lifestyle"].append("Practice regular breathing exercises")
            recommendations["herbal"].append("Arjuna for heart health")
        
        if "fast" in pulse_type.lower():
            recommendations["lifestyle"].append("Practice calming activities")
            recommendations["dietary"].append("Avoid stimulants like caffeine")
        
        return recommendations
    
    def _get_age_specific_recommendations(self, age: int, dominant_dosha: str) -> Dict[str, List[str]]:
        """Get age-specific recommendations"""
        recommendations = {"lifestyle": []}
        
        if age < 25:
            recommendations["lifestyle"].append("Focus on building healthy habits")
        elif age < 50:
            recommendations["lifestyle"].append("Balance work and personal life")
        else:
            recommendations["lifestyle"].append("Prioritize gentle, restorative practices")
        
        return recommendations
    
    def _merge_recommendations(self, base: Dict[str, List[str]], additional: Dict[str, List[str]]):
        """Merge additional recommendations into base"""
        for category, items in additional.items():
            if category in base:
                base[category].extend(items)
            else:
                base[category] = items
    
    def _get_precautions(self, imbalance: str, locale: str) -> List[str]:
        """Get precautions based on imbalance level"""
        if imbalance == "severe":
            return [
                "Severe imbalance detected. Please consult with an Ayurvedic practitioner.",
                "Follow recommendations carefully and monitor your symptoms."
            ]
        elif imbalance == "moderate":
            return [
                "Moderate imbalance detected. Follow the recommendations to restore balance.",
                "Monitor your symptoms and adjust as needed."
            ]
        else:
            return [
                "Mild imbalance detected. Follow the recommendations for optimal health."
            ]
    
    def _get_disclaimer(self, locale: str) -> str:
        """Get medical disclaimer"""
        return "This analysis is for educational purposes only and should not replace professional medical advice. Always consult with qualified healthcare practitioners for medical concerns."
    
    def _determine_prakriti(self, dosha_scores: Dict[str, float]) -> str:
        """Determine constitutional type"""
        sorted_doshas = sorted(dosha_scores.items(), key=lambda x: x[1], reverse=True)
        
        if len(sorted_doshas) >= 2:
            d1, s1 = sorted_doshas[0]
            d2, s2 = sorted_doshas[1]
            
            if s1 > 0.5:
                return d1.capitalize()
            elif s1 > 0.35 and s2 > 0.3:
                return f"{d1.capitalize()}-{d2.capitalize()}"
            else:
                return "Tridoshic"
        
        return "Unknown"
    
    def _generate_explanation(self, dosha_scores: Dict[str, float], 
                            dominant_dosha: str, imbalance: str, locale: str) -> str:
        """Generate explanation of diagnosis"""
        # Generate simple explanation
        scores_text = ", ".join([f"{d.capitalize()}: {s:.1%}" for d, s in dosha_scores.items()])
        return f"Your {dominant_dosha.capitalize()} dosha shows {imbalance} imbalance. Dosha distribution: {scores_text}"
    
    def _calculate_confidence(self, analyses: Dict[str, Any], weights: Dict[str, float]) -> float:
        """Calculate overall confidence score"""
        confidence = 0.5
        
        for analysis_type, weight in weights.items():
            if analysis_type in analyses:
                analysis = analyses[analysis_type]
                
                if analysis_type == "tongue":
                    conf = analysis.get("classification", {}).get("confidence", 0.5)
                elif analysis_type == "pulse":
                    conf = analysis.get("confidence", 0.5)
                elif analysis_type == "symptoms":
                    conf = analysis.get("confidence", 0.5)
                else:
                    conf = 0.5
                
                confidence += conf * weight * 0.5
        
        return min(confidence, 0.95)

# Global instance
consultation_service = ConsultationService()