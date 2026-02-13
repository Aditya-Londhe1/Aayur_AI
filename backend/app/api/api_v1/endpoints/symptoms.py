
from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import logging

from app.ai_models.symptom_analysis import symptom_analyzer

logger = logging.getLogger(__name__)
router = APIRouter()

class SymptomItem(BaseModel):
    name: str
    severity: Optional[str] = "mild"  # mild, moderate, severe
    duration: Optional[str] = ""
    description: Optional[str] = ""

class PatientInfo(BaseModel):
    age: Optional[int] = 30
    gender: Optional[str] = ""
    lifestyle: Optional[str] = ""
    medical_history: Optional[List[str]] = []

class SymptomAnalysisRequest(BaseModel):
    symptoms: List[SymptomItem]
    patient_info: Optional[PatientInfo] = None
    locale: Optional[str] = "en"

class LegacySymptomInput(BaseModel):
    """For backward compatibility"""
    text: str
    locale: Optional[str] = "en"

@router.post("/analyze", response_model=Dict[str, Any])
async def analyze_symptoms(request: SymptomAnalysisRequest):
    """
    Analyze symptoms to determine Dosha imbalance.
    
    Accepts structured symptom data with severity and duration.
    Returns detailed dosha analysis with recommendations.
    """
    try:
        if not request.symptoms:
            raise HTTPException(status_code=400, detail="No symptoms provided")
        
        # Convert Pydantic models to dictionaries
        symptoms_dict = [symptom.dict() for symptom in request.symptoms]
        patient_dict = request.patient_info.dict() if request.patient_info else {}
        
        # Perform analysis
        result = symptom_analyzer.analyze(symptoms_dict, patient_dict)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Add metadata
        result["request_id"] = f"SYM-{hash(str(symptoms_dict)) % 100000:05d}"
        result["locale"] = request.locale
        
        return {
            "success": True,
            "data": result,
            "message": "Symptom analysis completed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Symptom analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/analyze-text", response_model=Dict[str, Any])
async def analyze_symptoms_text(input_data: LegacySymptomInput):
    """
    Legacy endpoint: Analyze symptom description text.
    
    For backward compatibility with simple text input.
    """
    try:
        if not input_data.text.strip():
            raise HTTPException(status_code=400, detail="Empty text provided")
        
        # Convert text to structured format
        symptoms = [{
            "name": input_data.text,
            "severity": "moderate",
            "duration": "",
            "description": ""
        }]
        
        # Perform analysis
        result = symptom_analyzer.analyze(symptoms, {})
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "data": result,
            "message": "Text analysis completed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Text symptom analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/health")
async def symptom_service_health():
    """Health check for symptom analysis service"""
    try:
        # Check if analyzer is loaded
        is_loaded = symptom_analyzer.is_loaded
        method = "transformer" if symptom_analyzer.classifier is not None else "keyword"
        
        return {
            "service": "symptom_analysis",
            "status": "healthy",
            "model_loaded": is_loaded,
            "analysis_method": method,
            "transformers_available": symptom_analyzer.classifier is not None
        }
    except Exception as e:
        return {
            "service": "symptom_analysis", 
            "status": "unhealthy",
            "error": str(e)
        }
