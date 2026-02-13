# backend/app/services/consultation_store.py
"""
Global consultation storage
Ensures consultations persist across service instances
"""

# Global storage dictionary
_consultations = {}

def store_consultation(consultation_id: str, consultation: dict):
    """Store a consultation"""
    _consultations[consultation_id] = consultation

def get_consultation(consultation_id: str):
    """Retrieve a consultation"""
    return _consultations.get(consultation_id)

def update_consultation(consultation_id: str, consultation: dict):
    """Update a consultation"""
    _consultations[consultation_id] = consultation
    return consultation

def delete_consultation(consultation_id: str):
    """Delete a consultation"""
    if consultation_id in _consultations:
        del _consultations[consultation_id]

def list_consultations():
    """List all consultation IDs"""
    return list(_consultations.keys())

def clear_all():
    """Clear all consultations (for testing)"""
    _consultations.clear()
