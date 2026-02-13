from fastapi import APIRouter
from app.api.api_v1.endpoints import (
    tongue, 
    pulse, 
    symptoms, 
    diagnosis, 
    voice, 
    consultations, 
    voice_assistant,
    auth,
    users,
    feedback
)

api_router = APIRouter()

# Authentication routes (public)
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

# User management routes (protected)
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"]
)

# Diagnostic routes
api_router.include_router(pulse.router, prefix="/pulse", tags=["pulse"])
api_router.include_router(tongue.router, prefix="/tongue", tags=["tongue"])
api_router.include_router(symptoms.router, prefix="/symptoms", tags=["symptoms"])
api_router.include_router(diagnosis.router, prefix="/diagnosis", tags=["diagnosis"])

# Voice services
api_router.include_router(
    voice.router,
    prefix="/voice",
    tags=["Voice Services"]
)

api_router.include_router(
    voice_assistant.router,
    prefix="/voice-assistant",
    tags=["Voice Assistant"]
)

# Consultations
api_router.include_router(
    consultations.router,
    prefix="/consultations",
    tags=["Consultations"]
)

# Feedback
api_router.include_router(
    feedback.router,
    prefix="/feedback",
    tags=["Feedback"]
)
