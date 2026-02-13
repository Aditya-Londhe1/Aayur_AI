# backend/app/api/api_v1/endpoints/pulse.py
from fastapi import APIRouter, HTTPException, Form
from typing import Dict, Any, List
import logging
import numpy as np

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/generate-synthetic-pulse")
async def generate_synthetic_pulse(
    heart_rate: float = Form(...),
    duration: int = Form(60),
    sampling_rate: int = Form(50)
) -> Dict[str, Any]:
    """
    Generate synthetic pulse data for testing/demo purposes.
    
    WARNING: This is for DEMO/TESTING only!
    In production, pulse data should come from actual sensors/devices.
    
    Args:
        heart_rate: Target heart rate in BPM
        duration: Duration in seconds (default 60)
        sampling_rate: Sampling rate in Hz (default 50)
    
    Returns:
        Synthetic pulse waveform data
    """
    try:
        if heart_rate < 40 or heart_rate > 200:
            raise HTTPException(
                status_code=400,
                detail="Heart rate must be between 40 and 200 BPM"
            )
        
        if duration < 10 or duration > 300:
            raise HTTPException(
                status_code=400,
                detail="Duration must be between 10 and 300 seconds"
            )
        
        # Generate synthetic pulse waveform with dosha-specific characteristics
        total_points = duration * sampling_rate
        base_frequency = heart_rate / 60  # Convert BPM to Hz
        
        # Determine dosha characteristics based on heart rate
        if heart_rate > 85:
            # Vata: Fast, irregular, variable
            hrv_factor = 0.15  # High variability
            rhythm_irregularity = 0.20  # Irregular rhythm
            amplitude_variation = 0.25  # Variable amplitude
            noise_level = 0.15  # Higher noise
        elif heart_rate < 65:
            # Kapha: Slow, steady, regular
            hrv_factor = 0.03  # Low variability
            rhythm_irregularity = 0.02  # Very regular
            amplitude_variation = 0.05  # Stable amplitude
            noise_level = 0.05  # Low noise
        else:
            # Pitta: Moderate, strong, regular
            hrv_factor = 0.05  # Moderate variability
            rhythm_irregularity = 0.05  # Regular rhythm
            amplitude_variation = 0.10  # Moderate amplitude variation
            noise_level = 0.08  # Moderate noise
        
        wave = []
        phase = 0
        for i in range(total_points):
            t = i / sampling_rate
            
            # Add heart rate variability (beat-to-beat variation)
            hr_variation = np.random.normal(0, hrv_factor)
            current_frequency = base_frequency * (1 + hr_variation)
            
            # Add rhythm irregularity (timing variation)
            phase_jitter = np.random.normal(0, rhythm_irregularity)
            phase += 2 * np.pi * current_frequency / sampling_rate + phase_jitter
            
            # Add amplitude variation
            amplitude = 1.0 + np.random.normal(0, amplitude_variation)
            
            # Composite waveform: fundamental + harmonics + noise
            signal = amplitude * (
                np.sin(phase) +  # Fundamental with variable phase
                0.5 * np.sin(2 * phase) +  # Second harmonic
                0.3 * np.sin(3 * phase) +  # Third harmonic
                np.random.normal(0, noise_level)  # Noise
            )
            wave.append(float(signal))
        
        logger.info(f"Generated synthetic pulse: {heart_rate} BPM, {duration}s, {sampling_rate}Hz")
        
        return {
            "success": True,
            "pulse_data": wave,
            "metadata": {
                "heart_rate": heart_rate,
                "duration": duration,
                "sampling_rate": sampling_rate,
                "total_points": len(wave),
                "type": "synthetic",
                "warning": "This is synthetic data for demo purposes only"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Pulse generation error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate pulse data: {str(e)}"
        )

@router.post("/validate-pulse-data")
async def validate_pulse_data(
    pulse_data: str = Form(...),
    sampling_rate: int = Form(50)
) -> Dict[str, Any]:
    """
    Validate pulse data format and quality.
    
    Args:
        pulse_data: JSON string of pulse waveform
        sampling_rate: Sampling rate in Hz (default 50)
    
    Returns:
        Validation results
    """
    try:
        import json
        
        # Parse pulse data
        try:
            pulse_array = json.loads(pulse_data)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Invalid JSON format for pulse data"
            )
        
        if not isinstance(pulse_array, list):
            raise HTTPException(
                status_code=400,
                detail="Pulse data must be an array"
            )
        
        # Calculate actual duration from data
        actual_points = len(pulse_array)
        actual_duration = actual_points / sampling_rate
        
        # Validate minimum length (at least 10 seconds)
        if actual_duration < 10:
            return {
                "valid": False,
                "error": f"Insufficient duration. Minimum 10 seconds required, got {actual_duration:.1f}s",
                "actual_points": actual_points,
                "actual_duration": actual_duration,
                "sampling_rate": sampling_rate
            }
        
        # Validate data types
        if not all(isinstance(x, (int, float)) for x in pulse_array[:100]):  # Check first 100
            return {
                "valid": False,
                "error": "Pulse data must contain only numbers",
                "actual_points": actual_points
            }
        
        # Calculate basic statistics
        pulse_np = np.array(pulse_array, dtype=np.float32)
        stats = {
            "mean": float(np.mean(pulse_np)),
            "std": float(np.std(pulse_np)),
            "min": float(np.min(pulse_np)),
            "max": float(np.max(pulse_np)),
            "range": float(np.max(pulse_np) - np.min(pulse_np))
        }
        
        return {
            "valid": True,
            "actual_points": actual_points,
            "actual_duration": actual_duration,
            "sampling_rate": sampling_rate,
            "statistics": stats,
            "quality": "good" if stats["std"] > 0.1 else "low_variance"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Pulse validation error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Validation failed: {str(e)}"
        )

@router.get("/sensor-integration-guide")
async def get_sensor_integration_guide() -> Dict[str, Any]:
    """
    Get guide for integrating real pulse sensors.
    """
    return {
        "title": "Pulse Sensor Integration Guide",
        "overview": "For production use, integrate real pulse sensors instead of synthetic data",
        "supported_sensors": [
            {
                "name": "Photoplethysmography (PPG)",
                "description": "Optical sensor measuring blood volume changes",
                "examples": ["MAX30102", "MAX30100", "Pulse Sensor Amped"],
                "sampling_rate": "50-125 Hz recommended",
                "connection": "I2C, SPI, or Analog"
            },
            {
                "name": "ECG Sensors",
                "description": "Electrical activity of the heart",
                "examples": ["AD8232", "ADS1292R"],
                "sampling_rate": "250-500 Hz recommended",
                "connection": "SPI or Analog"
            },
            {
                "name": "Smartwatch/Wearable APIs",
                "description": "Data from consumer wearables",
                "examples": ["Apple HealthKit", "Google Fit", "Fitbit API"],
                "sampling_rate": "Varies by device",
                "connection": "REST API"
            }
        ],
        "data_format": {
            "required_fields": ["pulse_data", "heart_rate", "sampling_rate", "duration"],
            "pulse_data_format": "Array of float values representing waveform",
            "example": {
                "pulse_data": [0.1, 0.2, 0.3, "..."],
                "heart_rate": 75,
                "sampling_rate": 50,
                "duration": 60
            }
        },
        "integration_steps": [
            "1. Connect sensor to microcontroller/device",
            "2. Sample pulse waveform at 50+ Hz",
            "3. Collect 60 seconds of data (3000+ points)",
            "4. Send data to /consultations/complete endpoint",
            "5. Include heart_rate parameter for validation"
        ],
        "best_practices": [
            "Ensure stable sensor contact with skin",
            "Filter out motion artifacts",
            "Validate data quality before sending",
            "Include metadata (timestamp, sensor type)",
            "Handle sensor disconnection gracefully"
        ]
    }

@router.get("/health")
async def pulse_endpoint_health() -> Dict[str, Any]:
    """Health check for pulse endpoints"""
    return {
        "service": "pulse_endpoints",
        "status": "healthy",
        "endpoints": [
            "/generate-synthetic-pulse",
            "/validate-pulse-data",
            "/sensor-integration-guide"
        ]
    }
