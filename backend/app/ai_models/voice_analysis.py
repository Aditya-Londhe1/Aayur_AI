
import librosa
import numpy as np
import speech_recognition as sr
import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)

class VoiceAnalyzer:
    """
    Analyzes voice audio for Ayurvedic Dosha detection using acoustic features.
    Extracts Pitch, Energy, Spectral Centroid, and Speaking Rate.
    """

    def __init__(self):
        self.recognizer = sr.Recognizer()

    def analyze(self, audio_path: str) -> Dict[str, Any]:
        """
        Perform complete voice analysis: Acoustic Features + Transcription + Dosha Prediction
        """
        try:
            # 1. Acoustic Feature Extraction
            features = self._extract_acoustic_features(audio_path)
            
            # 2. Dosha Prediction
            dosha_result = self._predict_dosha(features)
            
            # 3. Speech-to-Text
            transcript = self._transcribe(audio_path)
            
            return {
                "acoustic_features": features,
                "dosha_prediction": dosha_result,
                "transcript": transcript,
                "success": True
            }
        except Exception as e:
            logger.error(f"Voice analysis failed: {e}")
            return {"success": False, "error": str(e)}

    def _extract_acoustic_features(self, audio_path: str) -> Dict[str, float]:
        y, sr = librosa.load(audio_path)
        
        # Pitch (Fundamental Frequency F0)
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        pitch_mean = np.mean(pitches[pitches > 0]) if np.any(pitches > 0) else 0
        
        # Spectral Centroid (Timbre/Brightness)
        centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
        
        # Jitter/Shimmer proxies (Variability)
        # Simplified: using standard deviation of pitch
        pitch_std = np.std(pitches[pitches > 0]) if np.any(pitches > 0) else 0

        # Energy (RMS)
        rms = np.mean(librosa.feature.rms(y=y))
        
        # Tempo/Speed
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)[0]

        return {
            "pitch_mean": float(pitch_mean),
            "pitch_std": float(pitch_std),
            "spectral_centroid": float(centroid),
            "energy": float(rms),
            "tempo": float(tempo)
        }

    def _predict_dosha(self, features: Dict[str, float]) -> Dict[str, Any]:
        scores = {"Vata": 0.0, "Pitta": 0.0, "Kapha": 0.0}
        
        # Vata: High pitch, variable speed, fast
        if features["pitch_mean"] > 200: scores["Vata"] += 0.3
        if features["tempo"] > 120: scores["Vata"] += 0.3
        if features["pitch_std"] > 50: scores["Vata"] += 0.2 # High variability

        # Pitta: Moderate speed, sharp/loud (High energy, high centroid)
        if 150 < features["pitch_mean"] < 250: scores["Pitta"] += 0.2
        if features["energy"] > 0.1: scores["Pitta"] += 0.4 # Loud
        if features["spectral_centroid"] > 2000: scores["Pitta"] += 0.3 # Sharp tone

        # Kapha: Low pitch, slow, stable
        if features["pitch_mean"] < 150: scores["Kapha"] += 0.4
        if features["tempo"] < 100: scores["Kapha"] += 0.3
        if features["pitch_std"] < 20: scores["Kapha"] += 0.3 # Monotone

        # Normalize
        total = sum(scores.values())
        if total > 0:
            scores = {k: v/total for k, v in scores.items()}
        
        dominant = max(scores, key=scores.get)
        
        return {
            "dominant_dosha": dominant,
            "confidence": scores[dominant],
            "scores": scores
        }

    def _transcribe(self, audio_path: str) -> str:
        try:
            with sr.AudioFile(audio_path) as source:
                audio = self.recognizer.record(source)
            text = self.recognizer.recognize_google(audio)
            return text
        except Exception as e:
            logger.warning(f"Transcription failed: {e}")
            return ""

voice_analyzer = VoiceAnalyzer()
