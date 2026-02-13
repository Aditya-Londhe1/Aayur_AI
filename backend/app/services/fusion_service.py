
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class FusionService:
    """
    Dosha Fusion Engine.
    Combines results from Pulse, Tongue, and Symptom analysis using a Weighted Average Strategy.
    """
    
    def __init__(self):
        # Weights for each modality
        # Tongue diagnosis is given highest weight as it's most reliable and visible in Ayurveda
        # Pulse is secondary but important, and symptoms provide supporting information
        self.weights = {
            "tongue": 0.50,    # 50% - Visual diagnosis, most reliable and objective
            "pulse": 0.30,     # 30% - Nadi Pariksha, important secondary indicator
            "symptoms": 0.20   # 20% - Patient-reported, subjective but valuable
        }
        
    def fuse_dosha_scores(self, analyses: Dict[str, Any], weights: Dict[str, float]) -> Dict[str, float]:
        """
        Fuse dosha scores from multiple analyses with given weights
        
        Args:
            analyses: Dictionary with analysis results
            weights: Dictionary with weights for each analysis type
            
        Returns:
            Dictionary with fused dosha scores
        """
        # Initialize fused scores
        fused_scores = {"vata": 0.0, "pitta": 0.0, "kapha": 0.0}
        
        # Process each analysis
        for analysis_type, weight in weights.items():
            if analysis_type in analyses:
                analysis = analyses[analysis_type]
                
                # Extract dosha scores based on analysis type
                if analysis_type == "symptoms":
                    scores = analysis.get("dosha_contributions", {})
                elif analysis_type == "tongue":
                    scores = analysis.get("dosha_scores", {})
                elif analysis_type == "pulse":
                    scores = analysis.get("probabilities", {})
                    # Convert keys to lowercase if needed
                    if "Vata" in scores:
                        scores = {k.lower(): v for k, v in scores.items()}
                else:
                    scores = {}
                
                # Add weighted scores
                for dosha in fused_scores:
                    dosha_score = scores.get(dosha, 0.0)
                    fused_scores[dosha] += dosha_score * weight
        
        # Normalize scores
        total = sum(fused_scores.values())
        if total > 0:
            fused_scores = {k: v/total for k, v in fused_scores.items()}
        
        return fused_scores

    def fuse_results(self, pulse_result: Dict, tongue_result: Dict, symptom_result: Dict) -> Dict[str, Any]:
        """
        Fuse results from multiple sources.
        Expects each input to be a dictionary containing 'probabilities', 'scores', 'dosha_scores', or 'dosha_contributions'.
        """
        
        # Initialize fused scores (using Title Case)
        fused_scores = {
            "Vata": 0.0,
            "Pitta": 0.0,
            "Kapha": 0.0
        }
        
        # Helper to extract and normalize scores
        def get_normalized_scores(result, source_name):
            if not result:
                return {"Vata": 0.0, "Pitta": 0.0, "Kapha": 0.0}
            
            extracted = {}
            # Look for various keys used by different services
            if "probabilities" in result:
                extracted = result["probabilities"]
            elif "scores" in result:
                extracted = result["scores"]
            elif "dosha_scores" in result:
                extracted = result["dosha_scores"]
            elif "dosha_contributions" in result:
                extracted = result["dosha_contributions"]
            
            # Normalize to Title Case
            normalized = {}
            for k, v in extracted.items():
                if k.lower() == "vata":
                    normalized["Vata"] = float(v)
                elif k.lower() == "pitta":
                    normalized["Pitta"] = float(v)
                elif k.lower() == "kapha":
                    normalized["Kapha"] = float(v)
            
            # If empty after trying to extract (e.g. only prediction key exists), log warning
            if not normalized and source_name != "unknown":
                logger.warning(f"No valid scores found for {source_name}. Result keys: {result.keys()}")
                
            return normalized

        pulse_scores = get_normalized_scores(pulse_result, "pulse")
        tongue_scores = get_normalized_scores(tongue_result, "tongue")
        symptom_scores = get_normalized_scores(symptom_result, "symptoms")
        
        # Calculate Weighted Average
        for dosha in fused_scores:
            p_score = pulse_scores.get(dosha, 0.0)
            t_score = tongue_scores.get(dosha, 0.0)
            s_score = symptom_scores.get(dosha, 0.0)
            
            weighted_sum = (
                (p_score * self.weights["pulse"]) +
                (t_score * self.weights["tongue"]) +
                (s_score * self.weights["symptoms"])
            )
            
            fused_scores[dosha] = float(weighted_sum)
            
        # Normalize fused scores to sum to 1
        total_score = sum(fused_scores.values())
        if total_score > 0:
            for d in fused_scores:
                fused_scores[d] /= total_score
                
        # Determine dominant Dosha
        dominant_dosha = max(fused_scores, key=fused_scores.get)
        
        # Construct detailed response
        return {
            "dominant_dosha": dominant_dosha,
            "confidence": fused_scores[dominant_dosha],
            "fused_scores": fused_scores,
            "sources": {
                "pulse": pulse_scores,
                "tongue": tongue_scores,
                "symptoms": symptom_scores
            },
            "weights_used": self.weights
        }

fusion_service = FusionService()
