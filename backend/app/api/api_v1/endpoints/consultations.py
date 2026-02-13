# backend/app/api/api_v1/endpoints/consultations.py
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Optional, Dict, Any
import json
import uuid
import tempfile
import os
import logging

from app.services.consultation_service import consultation_service
from app.services.report_service import report_service
from app.services.ai_service import ai_service
from app.services.explainer_service import explainer_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/create")
async def create_consultation(
    patient_name: str = Form(...),
    patient_age: int = Form(30),
    patient_gender: str = Form(""),
    locale: str = Form("en")
) -> Dict[str, Any]:
    """Create a new consultation session"""
    try:
        patient_data = {
            "name": patient_name,
            "age": patient_age,
            "gender": patient_gender
        }
        
        consultation = await consultation_service.create_consultation(patient_data, locale)
        
        return {
            "success": True,
            "consultation_id": consultation["consultation_id"],
            "consultation": consultation,
            "message": "Consultation created successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to create consultation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create consultation: {str(e)}")

@router.post("/complete")
async def complete_consultation(
    patient_name: str = Form(...),
    patient_age: int = Form(30),
    patient_gender: str = Form(""),
    symptoms: str = Form("[]"),
    tongue_image: Optional[UploadFile] = File(None),
    pulse_data: str = Form("[]"),
    heart_rate: Optional[float] = Form(None),  # Add heart_rate parameter
    locale: str = Form("en")
) -> Dict[str, Any]:
    """Complete consultation with all analysis types"""
    try:
        # Parse input data
        try:
            symptom_list = json.loads(symptoms) if symptoms else []
            pulse_list = json.loads(pulse_data) if pulse_data else []
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON format: {str(e)}")
        
        # Save tongue image if provided
        tongue_image_path = None
        if tongue_image:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
                content = await tongue_image.read()
                temp_file.write(content)
                tongue_image_path = temp_file.name
        
        try:
            # Prepare patient data
            patient_data = {
                "name": patient_name,
                "age": patient_age,
                "gender": patient_gender,
                "symptoms": symptom_list
            }
            
            # Run complete AI analysis
            analysis = await ai_service.complete_analysis(
                patient_data=patient_data,
                tongue_image_path=tongue_image_path,
                pulse_data=pulse_list if pulse_list else None,
                heart_rate=heart_rate,  # Pass heart_rate
                locale=locale
            )
            
            # Generate explainability
            explainability = explainer_service.generate_comprehensive_explanation(analysis)
            analysis['explainability'] = explainability
            
            return {
                "success": True,
                "analysis": analysis,
                "message": "Consultation completed successfully"
            }
            
        finally:
            # Clean up temporary file
            if tongue_image_path and os.path.exists(tongue_image_path):
                os.unlink(tongue_image_path)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to complete consultation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to complete consultation: {str(e)}")

@router.post("/{consultation_id}/add-tongue")
async def add_tongue_analysis(
    consultation_id: str,
    tongue_image: UploadFile = File(...)
) -> Dict[str, Any]:
    """Add tongue analysis to existing consultation"""
    try:
        # Retrieve consultation
        consultation = await consultation_service.get_consultation(consultation_id)
        if not consultation:
            raise HTTPException(status_code=404, detail="Consultation not found")
        
        # Save image temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            content = await tongue_image.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Add tongue analysis
            consultation = await consultation_service.add_tongue_analysis(consultation, temp_file_path)
            
            return {
                "success": True,
                "consultation_id": consultation_id,
                "tongue_analysis": consultation["analyses"].get("tongue"),
                "message": "Tongue analysis added successfully"
            }
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add tongue analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add tongue analysis: {str(e)}")

@router.post("/{consultation_id}/add-pulse")
async def add_pulse_analysis(
    consultation_id: str,
    pulse_data: str = Form(...)
) -> Dict[str, Any]:
    """Add pulse analysis to existing consultation"""
    try:
        # Retrieve consultation
        consultation = await consultation_service.get_consultation(consultation_id)
        if not consultation:
            raise HTTPException(status_code=404, detail="Consultation not found")
        
        # Parse pulse data
        try:
            pulse_list = json.loads(pulse_data)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid pulse data format")
        
        if not pulse_list or len(pulse_list) < 50:
            raise HTTPException(status_code=400, detail="Insufficient pulse data")
        
        # Add pulse analysis
        consultation = await consultation_service.add_pulse_analysis(consultation, pulse_list)
        
        return {
            "success": True,
            "consultation_id": consultation_id,
            "pulse_analysis": consultation["analyses"].get("pulse"),
            "message": "Pulse analysis added successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add pulse analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add pulse analysis: {str(e)}")

@router.post("/{consultation_id}/add-symptoms")
async def add_symptom_analysis(
    consultation_id: str,
    symptoms: str = Form(...)
) -> Dict[str, Any]:
    """Add symptom analysis to existing consultation"""
    try:
        # Retrieve consultation
        consultation = await consultation_service.get_consultation(consultation_id)
        if not consultation:
            raise HTTPException(status_code=404, detail="Consultation not found")
        
        # Parse symptoms
        try:
            symptom_list = json.loads(symptoms)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid symptoms format")
        
        if not symptom_list:
            raise HTTPException(status_code=400, detail="No symptoms provided")
        
        # Add symptom analysis
        consultation = await consultation_service.add_symptom_analysis(consultation, symptom_list)
        
        return {
            "success": True,
            "consultation_id": consultation_id,
            "symptom_analysis": consultation["analyses"].get("symptoms"),
            "message": "Symptom analysis added successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add symptom analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add symptom analysis: {str(e)}")

@router.post("/{consultation_id}/generate-report")
async def generate_consultation_report(
    consultation_id: str,
    report_type: str = Form("json"),
    language: str = Form("en")
) -> Dict[str, Any]:
    """Generate report for consultation"""
    try:
        logger.info(f"Generating report for consultation: {consultation_id}")
        
        # Retrieve actual consultation
        consultation = await consultation_service.get_consultation(consultation_id)
        
        if not consultation:
            logger.error(f"Consultation not found: {consultation_id}")
            raise HTTPException(status_code=404, detail="Consultation not found")
        
        logger.info(f"Found consultation: {consultation_id}, analyses: {list(consultation.get('analyses', {}).keys())}")
        
        # Check if consultation has any analyses
        if not consultation.get("analyses"):
            logger.warning(f"No analyses available for consultation: {consultation_id}")
            raise HTTPException(status_code=400, detail="No analyses available for this consultation")
        
        # Finalize consultation (integrate all analyses)
        logger.info(f"Finalizing consultation: {consultation_id}")
        finalized = await consultation_service.finalize_consultation(consultation)
        
        logger.info(f"Consultation finalized: {consultation_id}")
        
        # Generate report from real data
        report = await report_service.generate_consultation_report(finalized)
        
        logger.info(f"Report generated successfully for: {consultation_id}")
        
        # Format response for frontend compatibility
        response = {
            "success": True,
            "analysis": {
                "diagnosis": finalized.get("diagnosis", finalized.get("final_diagnosis", {})),
                "recommendations": finalized.get("recommendations", {}),
                "confidence": finalized.get("confidence", finalized.get("confidence_score", 0.0)),
                "analyses": finalized.get("analyses", {}),
                "patient_info": finalized.get("patient_info", {})
            },
            "report": report,
            "message": "Report generated successfully"
        }
        
        logger.info(f"Response structure: diagnosis={bool(response['analysis'].get('diagnosis'))}, recommendations={bool(response['analysis'].get('recommendations'))}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate report: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")

@router.get("/health")
async def consultation_service_health() -> Dict[str, Any]:
    """Health check for consultation service"""
    try:
        return {
            "service": "consultation_service",
            "status": "healthy",
            "available_endpoints": [
                "create", "complete", "add-tongue", "add-pulse", 
                "add-symptoms", "generate-report"
            ]
        }
    except Exception as e:
        return {
            "service": "consultation_service",
            "status": "unhealthy", 
            "error": str(e)
        }