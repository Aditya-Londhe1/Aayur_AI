# backend/app/services/ai_service.py
import torch
import numpy as np
from PIL import Image
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio

from app.ai_models.tongue_classifier import tongue_service
from app.services.pulse_service import pulse_service
from app.ai_models.symptom_analysis import SymptomAnalyzer
from app.services.fusion_service import FusionService
from app.services.ayurvedic_remedies_service import ayurvedic_remedies_service
from app.i18n import t

logger = logging.getLogger(__name__)

class AIService:
    """Complete AI service for Ayurvedic diagnosis"""
    
    def __init__(self):
        self.tongue_service = tongue_service
        self.pulse_service = pulse_service
        self.symptom_service = SymptomAnalyzer()
        self.fusion_service = FusionService()
        
        logger.info("AIService initialized")
    
    async def analyze_tongue(self, image_path: str, locale: str = "en") -> Dict[str, Any]:
        """Analyze tongue image"""
        try:
            # Load image
            image = Image.open(image_path).convert("RGB")
            
            # Run analysis
            analysis = self.tongue_service.analyze(image)
            
            # Translate results if needed
            if locale != "en":
                analysis = await self._translate_analysis(analysis, locale)
            
            return {
                "success": True,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Tongue analysis error: {e}")
            return {
                "success": False,
                "error": str(e),
                "analysis": None
            }
    
    async def analyze_pulse(self, pulse_data: List[float], heart_rate: Optional[float] = None, locale: str = "en") -> Dict[str, Any]:
        """Analyze pulse data
        
        Args:
            pulse_data: Raw pulse signal data
            heart_rate: Expected heart rate in BPM (from user input)
            locale: Language locale
        """
        try:
            if len(pulse_data) < 50:
                return {
                    "success": False,
                    "error": t("pulse.insufficient_data", locale=locale),
                    "analysis": None
                }
            
            # Run analysis with expected BPM
            analysis = self.pulse_service.analyze_pulse(pulse_data, expected_bpm=heart_rate)
            
            # Translate if needed
            if locale != "en":
                analysis = await self._translate_analysis(analysis, locale)
            
            return {
                "success": True,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Pulse analysis error: {e}")
            return {
                "success": False,
                "error": str(e),
                "analysis": None
            }
    
    async def analyze_symptoms(self, symptoms: List[Dict], patient_info: Dict, locale: str = "en") -> Dict[str, Any]:
        """Analyze symptoms"""
        try:
            analysis = self.symptom_service.analyze(symptoms, patient_info)
            
            # Translate if needed
            if locale != "en":
                analysis = await self._translate_analysis(analysis, locale)
            
            return {
                "success": True,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Symptom analysis error: {e}")
            return {
                "success": False,
                "error": str(e),
                "analysis": None
            }
    
    async def complete_analysis(self, patient_data: Dict, tongue_image_path: Optional[str] = None, 
                               pulse_data: Optional[List[float]] = None, heart_rate: Optional[float] = None,
                               locale: str = "en") -> Dict[str, Any]:
        """Complete multi-modal analysis
        
        Args:
            patient_data: Patient information and symptoms
            tongue_image_path: Path to tongue image
            pulse_data: Raw pulse signal data
            heart_rate: Expected heart rate in BPM (from user input)
            locale: Language locale
        """
        try:
            results = {}
            weights = {}
            
            # Run analyses in parallel if possible
            tasks = []
            
            # Tongue analysis - Highest weight (most reliable in Ayurveda)
            if tongue_image_path:
                task = asyncio.create_task(self.analyze_tongue(tongue_image_path, locale))
                tasks.append(("tongue", task))
                weights["tongue"] = 0.4
            
            # Pulse analysis - Objective measurement
            if pulse_data and len(pulse_data) >= 50:
                task = asyncio.create_task(self.analyze_pulse(pulse_data, heart_rate, locale))
                tasks.append(("pulse", task))
                weights["pulse"] = 0.35
            
            # Symptom analysis - Patient-reported context
            if patient_data.get("symptoms"):
                task = asyncio.create_task(self.analyze_symptoms(
                    patient_data["symptoms"], patient_data, locale
                ))
                tasks.append(("symptoms", task))
                weights["symptoms"] = 0.25
            
            # Wait for all analyses
            for name, task in tasks:
                result = await task
                if result["success"]:
                    results[name] = result["analysis"]
                else:
                    logger.warning(f"{name} analysis failed: {result.get('error')}")
            
            # Integrate results
            final_diagnosis = self._integrate_analyses(results, weights)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(final_diagnosis, patient_data, locale)
            
            # Calculate confidence
            confidence = self._calculate_confidence(results, weights)
            
            # Create comprehensive response
            response = {
                "patient_info": patient_data,
                "analyses": results,
                "diagnosis": final_diagnosis,
                "recommendations": recommendations,
                "confidence": confidence,
                "timestamp": datetime.now().isoformat(),
                "consultation_id": f"AI-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Complete analysis error: {e}")
            raise
    
    def _integrate_analyses(self, analyses: Dict[str, Any], weights: Dict[str, float]) -> Dict[str, Any]:
        """Integrate multiple analysis results using fusion service"""
        
        # Log what we're fusing
        logger.info(f"Integrating analyses: {list(analyses.keys())}")
        for analysis_type, analysis in analyses.items():
            if analysis_type == "pulse":
                logger.info(f"Pulse probabilities: {analysis.get('probabilities', {})}")
            elif analysis_type == "tongue":
                logger.info(f"Tongue dosha_scores: {analysis.get('dosha_scores', {})}")
            elif analysis_type == "symptoms":
                logger.info(f"Symptom dosha_contributions: {analysis.get('dosha_contributions', {})}")
        
        # Use the fusion service for proper integration
        fusion_result = self.fusion_service.fuse_results(
            pulse_result=analyses.get("pulse", {}),
            tongue_result=analyses.get("tongue", {}),
            symptom_result=analyses.get("symptoms", {})
        )
        
        logger.info(f"Fusion result: {fusion_result}")
        
        # Extract fused scores (convert from Title Case to lowercase)
        dosha_scores = {
            "vata": fusion_result["fused_scores"].get("Vata", 0.0),
            "pitta": fusion_result["fused_scores"].get("Pitta", 0.0),
            "kapha": fusion_result["fused_scores"].get("Kapha", 0.0)
        }
        
        # Get dominant dosha from fusion result
        dominant_dosha = fusion_result["dominant_dosha"].lower()
        dominant_score = dosha_scores[dominant_dosha]
        
        # Determine imbalance level
        if dominant_score > 0.6:
            imbalance = "severe"
        elif dominant_score > 0.45:
            imbalance = "moderate"
        else:
            imbalance = "mild"
        
        # Determine prakriti type
        prakriti = self._determine_prakriti(dosha_scores)
        
        # Determine likely conditions
        conditions = self._identify_conditions(analyses)
        
        return {
            "dosha_scores": dosha_scores,
            "dominant_dosha": dominant_dosha,
            "imbalance_level": imbalance,
            "prakriti_type": prakriti,
            "vikriti_type": f"{dominant_dosha.capitalize()} imbalance",
            "likely_conditions": conditions,
            "explanation": self._generate_explanation(dosha_scores, dominant_dosha, imbalance, locale="en"),
            "fusion_details": {
                "sources": fusion_result.get("sources", {}),
                "weights_used": fusion_result.get("weights_used", {}),
                "fusion_confidence": fusion_result.get("confidence", 0.0)
            }
        }
    
    async def _generate_recommendations(self, diagnosis: Dict[str, Any], patient_data: Dict, locale: str) -> Dict[str, Any]:
        """Generate personalized recommendations including Ayurvedic home remedies"""
        dominant_dosha = diagnosis["dominant_dosha"]
        imbalance = diagnosis["imbalance_level"]
        age = patient_data.get("patient_age", 30)
        
        # Get Ayurvedic home remedies from dedicated service
        ayurvedic_remedies = ayurvedic_remedies_service.get_remedies_for_dosha(
            dominant_dosha, 
            imbalance
        )
        
        # Get basic recommendations
        recommendations = self._get_basic_recommendations(dominant_dosha, imbalance)
        
        # Add Ayurvedic home remedies as a new category
        recommendations["ayurvedic_home_remedies"] = ayurvedic_remedies["home_remedies"]
        recommendations["ayurvedic_dietary"] = ayurvedic_remedies["dietary_remedies"]
        recommendations["ayurvedic_lifestyle"] = ayurvedic_remedies["lifestyle_remedies"]
        recommendations["remedy_description"] = ayurvedic_remedies["description"]
        
        # Personalize based on symptoms
        symptoms = patient_data.get("symptoms", [])
        if symptoms:
            symptom_based = self._get_symptom_specific_recommendations(symptoms)
            
            # Merge recommendations
            for category in ["dietary", "lifestyle", "herbal", "yoga"]:
                if category in symptom_based:
                    if category in recommendations:
                        recommendations[category].extend(symptom_based[category])
                    else:
                        recommendations[category] = symptom_based[category]
            
            # Add symptom-specific Ayurvedic remedies
            symptom_remedies = []
            for symptom in symptoms[:3]:  # Top 3 symptoms
                # Handle both string and dict formats
                if isinstance(symptom, str):
                    symptom_name = symptom.lower()
                else:
                    symptom_name = symptom.get("name", "").lower()
                
                specific_remedies = ayurvedic_remedies_service.get_remedy_by_symptom(symptom_name)
                if specific_remedies:
                    symptom_remedies.extend(specific_remedies)
            
            if symptom_remedies:
                recommendations["symptom_specific_remedies"] = symptom_remedies
        
        # Limit number of recommendations per category
        for category in recommendations:
            if isinstance(recommendations[category], list) and category not in ["ayurvedic_home_remedies", "ayurvedic_dietary", "ayurvedic_lifestyle"]:
                recommendations[category] = recommendations[category][:10]
        
        return recommendations
    
    def _get_basic_recommendations(self, dominant_dosha: str, imbalance: str) -> Dict[str, List[str]]:
        """Get basic recommendations for dosha imbalance"""
        recommendations = {
            "vata": {
                "dietary": [
                    "Eat warm, cooked foods",
                    "Include healthy fats like ghee and sesame oil",
                    "Avoid cold, raw foods",
                    "Eat regular meals at consistent times",
                    "Include sweet, sour, and salty tastes"
                ],
                "lifestyle": [
                    "Maintain regular sleep schedule",
                    "Practice gentle, grounding exercises",
                    "Keep warm and avoid cold environments",
                    "Practice meditation and deep breathing",
                    "Establish daily routines"
                ],
                "herbal": [
                    "Ashwagandha for stress relief",
                    "Brahmi for mental clarity",
                    "Triphala for digestion",
                    "Sesame oil for massage"
                ],
                "yoga": [
                    "Gentle, slow-paced yoga",
                    "Sun salutations (slow)",
                    "Forward bends",
                    "Restorative poses"
                ]
            },
            "pitta": {
                "dietary": [
                    "Eat cooling foods",
                    "Avoid spicy, hot, and acidic foods",
                    "Include sweet, bitter, and astringent tastes",
                    "Drink plenty of cool water",
                    "Eat fresh fruits and vegetables"
                ],
                "lifestyle": [
                    "Avoid excessive heat and sun",
                    "Practice cooling breathing exercises",
                    "Maintain work-life balance",
                    "Avoid competitive activities when stressed",
                    "Take breaks during intense work"
                ],
                "herbal": [
                    "Aloe vera for cooling",
                    "Neem for purification",
                    "Coriander for digestion",
                    "Coconut oil for massage"
                ],
                "yoga": [
                    "Moderate-paced yoga",
                    "Moon salutations",
                    "Twisting poses",
                    "Cooling pranayama"
                ]
            },
            "kapha": {
                "dietary": [
                    "Eat light, warm, and spicy foods",
                    "Avoid heavy, oily, and cold foods",
                    "Include pungent, bitter, and astringent tastes",
                    "Reduce dairy and sugar intake",
                    "Eat smaller, more frequent meals"
                ],
                "lifestyle": [
                    "Engage in vigorous exercise",
                    "Wake up early",
                    "Stay active throughout the day",
                    "Avoid daytime napping",
                    "Seek stimulating environments"
                ],
                "herbal": [
                    "Ginger for digestion",
                    "Turmeric for inflammation",
                    "Trikatu for metabolism",
                    "Mustard oil for massage"
                ],
                "yoga": [
                    "Dynamic, energizing yoga",
                    "Sun salutations (vigorous)",
                    "Backbends",
                    "Energizing pranayama"
                ]
            }
        }
        
        return recommendations.get(dominant_dosha, recommendations["vata"])
    
    def _get_symptom_specific_recommendations(self, symptoms: List) -> Dict[str, List[str]]:
        """Get recommendations based on specific symptoms"""
        recommendations = {"dietary": [], "lifestyle": [], "herbal": [], "yoga": []}
        
        for symptom in symptoms:
            # Handle both string and dict formats
            if isinstance(symptom, str):
                symptom_name = symptom.lower()
            else:
                symptom_name = symptom.get("name", "").lower()
            
            if "headache" in symptom_name:
                recommendations["herbal"].append("Peppermint oil for headache relief")
                recommendations["lifestyle"].append("Practice stress management techniques")
            
            elif "digestive" in symptom_name or "stomach" in symptom_name:
                recommendations["dietary"].append("Eat easily digestible foods")
                recommendations["herbal"].append("Ginger tea for digestion")
            
            elif "sleep" in symptom_name or "insomnia" in symptom_name:
                recommendations["lifestyle"].append("Maintain regular sleep schedule")
                recommendations["herbal"].append("Chamomile tea before bed")
            
            elif "stress" in symptom_name or "anxiety" in symptom_name:
                recommendations["yoga"].append("Practice calming pranayama")
                recommendations["herbal"].append("Ashwagandha for stress relief")
        
        return recommendations
    
    def _calculate_confidence(self, analyses: Dict[str, Any], weights: Dict[str, float]) -> float:
        """Calculate overall confidence score"""
        confidence = 0.5  # Base confidence
        
        # Add confidence based on available analyses
        for analysis_type, weight in weights.items():
            if analysis_type in analyses:
                analysis = analyses[analysis_type]
                
                # Get confidence from each analysis
                if analysis_type == "tongue":
                    conf = analysis.get("classification", {}).get("confidence", 0.0)
                elif analysis_type == "pulse":
                    conf = analysis.get("confidence", 0.0)
                elif analysis_type == "symptoms":
                    conf = analysis.get("confidence", 0.0)
                else:
                    conf = 0.5
                
                confidence += conf * weight * 0.5
        
        # Cap at 0.95
        return min(confidence, 0.95)
    
    def _determine_prakriti(self, dosha_scores: Dict[str, float]) -> str:
        """Determine Ayurvedic constitution type"""
        sorted_doshas = sorted(dosha_scores.items(), key=lambda x: x[1], reverse=True)
        
        if len(sorted_doshas) >= 2:
            d1, s1 = sorted_doshas[0]
            d2, s2 = sorted_doshas[1]
            
            if s1 > 0.5:
                return d1.capitalize()
            elif s1 > 0.35 and s2 > 0.3:
                return f"{d1.capitalize()}-{d2.capitalize()}"
            else:
                return "Tridoshic (Balanced)"
        
        return "Unknown"
    
    def _identify_conditions(self, analyses: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify likely conditions"""
        conditions = []
        
        # Check symptom analysis for conditions
        if "symptoms" in analyses:
            symptom_analysis = analyses["symptoms"]
            if "likely_conditions" in symptom_analysis:
                conditions.extend(symptom_analysis["likely_conditions"])
        
        # Check tongue analysis for specific signs
        if "tongue" in analyses:
            tongue_analysis = analyses["tongue"]
            features = tongue_analysis.get("detailed_features", {})
            
            # Based on tongue signs
            if features.get("cracks", {}).get("present"):
                conditions.append({
                    "name": "Vata Imbalance Disorder",
                    "confidence": features["cracks"]["severity"],
                    "description": "Cracks on tongue indicate Vata imbalance"
                })
            
            if features.get("coating", {}).get("type") == "thick_white":
                conditions.append({
                    "name": "Kapha Imbalance Disorder",
                    "confidence": 0.7,
                    "description": "Thick white coating indicates Kapha imbalance"
                })
        
        return conditions[:5]  # Return top 5 conditions
    
    def _generate_explanation(self, dosha_scores: Dict[str, float], dominant_dosha: str, 
                            imbalance: str, locale: str = "en") -> str:
        """Generate human-readable explanation"""
        explanations = {
            "en": f"Based on the analysis, you have a {imbalance} {dominant_dosha} dosha imbalance. "
                  f"This indicates that the {dominant_dosha} energy in your body is predominant, "
                  f"which may lead to specific health concerns. The recommendations focus on "
                  f"balancing {dominant_dosha} through diet, lifestyle, and herbal interventions.",
            
            "hi": f"विश्लेषण के आधार पर, आपमें {imbalance} {dominant_dosha} दोष असंतुलन है। "
                  f"इसका मतलब है कि आपके शरीर में {dominant_dosha} ऊर्जा प्रबल है, "
                  f"जिससे विशेष स्वास्थ्य समस्याएं हो सकती हैं। सुझाव {dominant_dosha} को "
                  f"संतुलित करने पर केंद्रित हैं।",
            
            "ta": f"பகுப்பாய்வின் படி, உங்களுக்கு {imbalance} {dominant_dosha} தோசா சமநிலையின்மை உள்ளது. "
                  f"இது உங்கள் உடலில் {dominant_dosha} ஆற்றல் ஆதிக்கம் செலுத்துவதைக் குறிக்கிறது, "
                  f"இது குறிப்பிட்ட சுகாதார பிரச்சினைகளுக்கு வழிவகுக்கும். பரிந்துரைகள் "
                  f"{dominant_dosha} சமநிலைப்படுத்துவதில் கவனம் செலுத்துகின்றன."
        }
        
        return explanations.get(locale, explanations["en"])
    
    async def _translate_analysis(self, analysis: Dict[str, Any], target_locale: str) -> Dict[str, Any]:
        """Translate analysis results to target locale"""
        # This would use a translation service
        # For now, return as-is with locale tag
        analysis["locale"] = target_locale
        return analysis

# Global instance
ai_service = AIService()