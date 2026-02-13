from fastapi import APIRouter, UploadFile, File
from PIL import Image
import io

from app.ai_models.tongue_classifier import tongue_service

router = APIRouter()

@router.post("/analyze")
async def analyze_tongue(file: UploadFile = File(...)):
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    return tongue_service.analyze(image)
