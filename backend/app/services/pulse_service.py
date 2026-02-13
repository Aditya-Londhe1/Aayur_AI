
import torch
import numpy as np
import os
import logging
from scipy.signal import butter, filtfilt, find_peaks
from typing import Dict, Any, List

from app.ai_models.pulse.pulse_model import PulseBiLSTM
from app.ai_models.pulse.dosha_mapper import AyurvedicPulseMapper
from app.core.config import settings

logger = logging.getLogger(__name__)

class PulseService:
    def __init__(self):
        self.model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.sampling_rate = 125  # Default for BIDMC
        
    def load_model(self, model_path: str = None):
        """Load the trained model"""
        if model_path is None:
            # Default path
            model_path = os.path.join(settings.BASE_DIR, "models/pulse/final_model.pth")
            
        if not os.path.exists(model_path):
            logger.warning(f"Pulse model not found at {model_path}. Using random weights for dev.")
            self.model = PulseBiLSTM(feature_dim=3) # Assuming feature_dim=3 as per training
            self.model.to(self.device)
            self.model.eval()
            return

        try:
            checkpoint = torch.load(model_path, map_location=self.device)
            self.model = PulseBiLSTM(feature_dim=3)
            if 'model_state_dict' in checkpoint:
                self.model.load_state_dict(checkpoint['model_state_dict'])
            else:
                self.model.load_state_dict(checkpoint)
            
            self.model.to(self.device)
            self.model.eval()
            logger.info(f"Pulse model loaded from {model_path}")
        except Exception as e:
            logger.error(f"Failed to load pulse model: {e}")
            raise

    def analyze_pulse(self, signal_data: List[float], expected_bpm: float = None) -> Dict[str, Any]:
        """
        Analyze pulse signal data with Ayurvedic interpretation.
        Args:
            signal_data: Raw pulse signal
            expected_bpm: Expected BPM from user input (optional, for validation)
        """
        if self.model is None:
            self.load_model()
            
        # Preprocess
        signal = np.array(signal_data, dtype=np.float32)
        filtered_signal = self._bandpass_filter(signal)
        
        # Feature Extraction
        features = self._extract_features(filtered_signal, expected_bpm=expected_bpm)
        
        # Prepare for model
        # Segment into windows if needed, but for single prediction we might take a fixed length
        # For simplicity, let's take the first 10s (1250 samples) or pad/truncate
        window_size = 1250
        if len(filtered_signal) < window_size:
            # Pad
            padded = np.zeros(window_size, dtype=np.float32)
            padded[:len(filtered_signal)] = filtered_signal
            segment = padded
        else:
            segment = filtered_signal[:window_size]
            
        # Model input
        signal_tensor = torch.tensor(segment, dtype=torch.float32).unsqueeze(0).unsqueeze(0) # [1, 1, T]
        feature_tensor = torch.tensor([
            features["heart_rate"], 
            features["hrv"], 
            features["lf_hf_ratio"]
        ], dtype=torch.float32).unsqueeze(0) # [1, 3]
        
        signal_tensor = signal_tensor.to(self.device)
        feature_tensor = feature_tensor.to(self.device)
        
        # Inference
        with torch.no_grad():
            outputs = self.model(signal_tensor, feature_tensor)
            
        # Post-process
        main_logits = outputs['main']
        probs = torch.softmax(main_logits, dim=1).cpu().numpy()[0]
        prediction = int(np.argmax(probs))
        
        dosha_map = {0: "Vata", 1: "Pitta", 2: "Kapha", 3: "Balanced"}
        
        # Basic ML prediction
        ml_prediction = {
            "prediction": dosha_map.get(prediction, "Unknown"),
            "confidence": float(probs[prediction]),
            "probabilities": {
                "Vata": float(probs[0]),
                "Pitta": float(probs[1]),
                "Kapha": float(probs[2]),
                "Balanced": float(probs[3])
            },
            "features": features
        }
        
        # ============ USE AYURVEDIC DOSHA MAPPER ============
        # Map features to traditional Ayurvedic interpretation
        ayurvedic_analysis = AyurvedicPulseMapper.map_features_to_dosha(features)
        
        # Combine ML prediction with Ayurvedic knowledge
        # Use ML probabilities but enrich with Ayurvedic interpretation
        combined_result = {
            # ML predictions (for fusion engine)
            "prediction": ml_prediction["prediction"],
            "confidence": ml_prediction["confidence"],
            "probabilities": ml_prediction["probabilities"],
            
            # Ayurvedic interpretation
            "ayurvedic_analysis": {
                "dominant_dosha": ayurvedic_analysis["dominant_dosha"],
                "secondary_dosha": ayurvedic_analysis["secondary_dosha"],
                "dosha_combination": ayurvedic_analysis["dosha_combination"],
                "traditional_characteristics": ayurvedic_analysis["traditional_characteristics"],
                "interpretation": ayurvedic_analysis["interpretation"],
                "recommendations": ayurvedic_analysis["recommendations"],
                "ayurvedic_insights": ayurvedic_analysis["ayurvedic_insights"]
            },
            
            # Technical features
            "features": features,
            
            # Pulse positions (traditional Nadi Pariksha)
            "pulse_positions": ayurvedic_analysis["pulse_positions"]
        }
        
        logger.info(f"Pulse Analysis Complete - ML: {ml_prediction['prediction']}, "
                   f"Ayurvedic: {ayurvedic_analysis['dominant_dosha'].capitalize()}")
        
        return combined_result

    def _bandpass_filter(self, signal: np.ndarray) -> np.ndarray:
        nyq = 0.5 * self.sampling_rate
        b, a = butter(3, [0.5 / nyq, 5.0 / nyq], btype="band")
        return filtfilt(b, a, signal).astype(np.float32)

    def _extract_features(self, signal: np.ndarray, expected_bpm: float = None) -> Dict[str, float]:
        """Extract comprehensive features from pulse signal for Ayurvedic analysis.
        
        Args:
            signal: Filtered pulse signal
            expected_bpm: Expected BPM from user input (if available, use this instead of calculating)
        """
        from scipy import stats
        
        peaks, peak_properties = find_peaks(signal, distance=0.4 * self.sampling_rate, prominence=0.1)
        
        if len(peaks) < 2:
            # Use expected BPM if provided, otherwise default
            heart_rate = expected_bpm if expected_bpm is not None else 70.0
            return {
                "heart_rate": float(heart_rate), 
                "hrv": 0.0, 
                "lf_hf_ratio": 0.0,
                "rhythm_type": "insufficient_data",
                "mean_peak_amplitude": 0.0,
                "sample_entropy": 0.0,
                "pitta_score": 0.0,
                "std_rr": 0.0,
                "vlf_power": 0.0,
                "has_stress_indicator": False
            }
            
        rr_intervals = np.diff(peaks) / self.sampling_rate
        
        # Use expected BPM if provided, otherwise calculate from signal
        if expected_bpm is not None:
            heart_rate = expected_bpm
        else:
            heart_rate = 60.0 / np.mean(rr_intervals)
            
        # Heart Rate Variability
        hrv = np.std(rr_intervals)
        std_rr = float(hrv)  # Standard deviation of RR intervals
        
        # Frequency domain analysis
        if len(rr_intervals) > 10:
            rr_fft = np.abs(np.fft.rfft(rr_intervals - np.mean(rr_intervals)))
            freqs = np.fft.rfftfreq(len(rr_intervals), d=np.mean(rr_intervals))
            
            # Very Low Frequency (VLF): 0.003-0.04 Hz - Kapha indicator
            vlf = np.sum(rr_fft[(freqs >= 0.003) & (freqs < 0.04)])
            
            # Low Frequency (LF): 0.04-0.15 Hz - Sympathetic activity
            lf = np.sum(rr_fft[(freqs >= 0.04) & (freqs < 0.15)])
            
            # High Frequency (HF): 0.15-0.4 Hz - Parasympathetic activity
            hf = np.sum(rr_fft[(freqs >= 0.15) & (freqs < 0.4)])
            
            lf_hf_ratio = float(lf / (hf + 1e-6))
            vlf_power = float(vlf)
        else:
            lf_hf_ratio = 0.0
            vlf_power = 0.0
        
        # Rhythm regularity - Vata indicator
        if len(rr_intervals) > 5:
            # Calculate coefficient of variation
            cv = (np.std(rr_intervals) / np.mean(rr_intervals)) * 100
            if cv > 10:
                rhythm_type = "irregular"
            elif cv < 5:
                rhythm_type = "regular"
            else:
                rhythm_type = "moderate"
        else:
            rhythm_type = "insufficient_data"
        
        # Peak amplitude analysis - Pitta indicator
        if 'prominences' in peak_properties:
            prominences = peak_properties['prominences']
            mean_peak_amplitude = float(np.mean(prominences))
            
            # Pitta score based on amplitude and sharpness
            # Higher amplitude and sharper peaks indicate Pitta
            pitta_score = mean_peak_amplitude * 100
        else:
            # Calculate amplitude from signal at peak locations
            peak_amplitudes = signal[peaks]
            mean_peak_amplitude = float(np.mean(np.abs(peak_amplitudes)))
            pitta_score = mean_peak_amplitude * 100
        
        # Sample Entropy - complexity measure (Vata indicator)
        try:
            sample_entropy = self._calculate_sample_entropy(rr_intervals)
        except:
            sample_entropy = 0.0
        
        # Stress indicator
        # High LF/HF ratio (>2) or very high HR (>90) suggests stress
        has_stress_indicator = (lf_hf_ratio > 2.0) or (heart_rate > 90)
        
        return {
            # Basic features
            "heart_rate": float(heart_rate),
            "hrv": float(hrv),
            "lf_hf_ratio": lf_hf_ratio,
            
            # Rhythm features (Vata)
            "rhythm_type": rhythm_type,
            "std_rr": std_rr,
            "sample_entropy": float(sample_entropy),
            
            # Amplitude features (Pitta)
            "mean_peak_amplitude": mean_peak_amplitude,
            "pitta_score": pitta_score,
            
            # Frequency features (Kapha)
            "vlf_power": vlf_power,
            
            # Additional indicators
            "has_stress_indicator": has_stress_indicator,
            "num_peaks": len(peaks),
            "signal_duration": len(signal) / self.sampling_rate
        }
    
    def _calculate_sample_entropy(self, data: np.ndarray, m: int = 2, r: float = 0.2) -> float:
        """
        Calculate Sample Entropy - measure of signal complexity
        Higher entropy indicates more irregular/complex patterns (Vata)
        
        Args:
            data: Time series data (RR intervals)
            m: Pattern length
            r: Tolerance (as fraction of std)
        """
        N = len(data)
        if N < m + 1:
            return 0.0
        
        # Normalize
        data = np.array(data)
        std = np.std(data)
        if std == 0:
            return 0.0
        
        r = r * std
        
        def _maxdist(xi, xj):
            return max([abs(ua - va) for ua, va in zip(xi, xj)])
        
        def _phi(m):
            patterns = np.array([data[i:i + m] for i in range(N - m)])
            C = np.zeros(N - m)
            for i in range(N - m):
                for j in range(N - m):
                    if i != j and _maxdist(patterns[i], patterns[j]) <= r:
                        C[i] += 1
            return np.sum(C) / (N - m)
        
        try:
            phi_m = _phi(m)
            phi_m1 = _phi(m + 1)
            
            if phi_m == 0 or phi_m1 == 0:
                return 0.0
            
            return -np.log(phi_m1 / phi_m)
        except:
            return 0.0

pulse_service = PulseService()
