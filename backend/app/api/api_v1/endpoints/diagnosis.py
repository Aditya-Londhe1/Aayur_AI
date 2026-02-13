
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from typing import Dict, Any, Optional
from pydantic import BaseModel
import logging
import os

from app.services.fusion_service import fusion_service
from app.services.pdf_report_service import pdf_report_service
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter()

logger = logging.getLogger(__name__)

class DiagnosisRequest(BaseModel):
    pulse_result: Optional[Dict[str, Any]] = None
    tongue_result: Optional[Dict[str, Any]] = None
    symptoms_result: Optional[Dict[str, Any]] = None

@router.post("/final", response_model=Dict[str, Any])
async def generate_diagnosis(request: DiagnosisRequest):
    """
    Generate final diagnosis by fusing results from Pulse, Tongue, and Symptom analysis.
    """
    try:
        # Validate that at least one input is provided
        if not any([request.pulse_result, request.tongue_result, request.symptoms_result]):
             # If no inputs, return a default empty response or error
             # Ideally we want at least one source
             return {
                 "dominant_dosha": "Unknown",
                 "confidence": 0.0,
                 "message": "No analysis results provided provided for fusion."
             }

        result = fusion_service.fuse_results(
            pulse_result=request.pulse_result,
            tongue_result=request.tongue_result,
            symptom_result=request.symptoms_result
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error generating diagnosis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-pdf")
async def generate_pdf_report(
    diagnosis_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """
    Generate a PDF report from diagnosis data
    
    Requires authentication
    """
    try:
        logger.info(f"Generating PDF for user: {current_user.username}")
        logger.info(f"Diagnosis data keys: {list(diagnosis_data.keys())}")
        
        # Prepare user info
        user_info = {
            'full_name': current_user.full_name or current_user.username,
            'email': current_user.email
        }
        
        # Generate PDF
        pdf_path = pdf_report_service.generate_pdf_report(diagnosis_data, user_info)
        
        # Return PDF file
        if os.path.exists(pdf_path):
            logger.info(f"PDF generated successfully: {pdf_path}")
            return FileResponse(
                pdf_path,
                media_type='application/pdf',
                filename=os.path.basename(pdf_path)
            )
        else:
            logger.error(f"PDF file not found: {pdf_path}")
            raise HTTPException(status_code=500, detail="Failed to generate PDF")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating PDF report: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")
