import numpy as np
from scipy import signal, stats
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class PulseFeatureExtractor:
    """
    Pure pulse feature extractor.
    No classification. No dosha rules.
    Outputs only numeric features for fusion & explainability.
    """

    def __init__(self, sampling_rate: int = 125):
        self.sampling_rate = sampling_rate

    # ----------------------------------------------------
    # TIME DOMAIN FEATURES
    # ----------------------------------------------------
    def extract_time_domain_features(self, pulse: np.ndarray) -> Dict[str, float]:
        features = {}

        features["mean"] = float(np.mean(pulse))
        features["std"] = float(np.std(pulse))
        features["min"] = float(np.min(pulse))
        features["max"] = float(np.max(pulse))
        features["range"] = features["max"] - features["min"]
        features["rms"] = float(np.sqrt(np.mean(pulse ** 2)))

        # Peak detection
        peaks, props = signal.find_peaks(
            pulse,
            height=np.mean(pulse) + 0.5 * np.std(pulse),
            distance=self.sampling_rate // 4,
        )

        if len(peaks) > 1:
            rr = np.diff(peaks) / self.sampling_rate * 1000.0

            features["mean_rr"] = float(np.mean(rr))
            features["std_rr"] = float(np.std(rr))
            features["rmssd"] = float(np.sqrt(np.mean(np.diff(rr) ** 2)))

            features["heart_rate"] = float(60000.0 / np.mean(rr))

            peak_heights = props["peak_heights"]
            features["mean_peak_amplitude"] = float(np.mean(peak_heights))
            features["std_peak_amplitude"] = float(np.std(peak_heights))
        else:
            features.update({
                "mean_rr": 0.0,
                "std_rr": 0.0,
                "rmssd": 0.0,
                "heart_rate": 0.0,
                "mean_peak_amplitude": 0.0,
                "std_peak_amplitude": 0.0,
            })

        features["snr"] = self._signal_to_noise_ratio(pulse)
        features["baseline_wander"] = self._baseline_wander(pulse)

        return features

    # ----------------------------------------------------
    # FREQUENCY DOMAIN FEATURES
    # ----------------------------------------------------
    def extract_frequency_domain_features(self, pulse: np.ndarray) -> Dict[str, float]:
        features = {}

        freqs, psd = signal.welch(
            pulse,
            fs=self.sampling_rate,
            nperseg=min(256, len(pulse)),
        )

        vlf = self._band_power(freqs, psd, (0.003, 0.04))
        lf = self._band_power(freqs, psd, (0.04, 0.15))
        hf = self._band_power(freqs, psd, (0.15, 0.4))
        total = vlf + lf + hf

        features["vlf_power"] = float(vlf)
        features["lf_power"] = float(lf)
        features["hf_power"] = float(hf)
        features["total_power"] = float(total)

        if total > 0:
            features["lf_hf_ratio"] = float(lf / hf) if hf > 0 else 0.0
            features["lf_nu"] = float(lf / total)
            features["hf_nu"] = float(hf / total)
        else:
            features["lf_hf_ratio"] = 0.0
            features["lf_nu"] = 0.0
            features["hf_nu"] = 0.0

        dominant_idx = np.argmax(psd)
        features["dominant_frequency"] = float(freqs[dominant_idx])

        return features

    # ----------------------------------------------------
    # MASTER FEATURE FUNCTION
    # ----------------------------------------------------
    def extract_all_features(self, pulse: np.ndarray) -> Dict[str, float]:
        if pulse.ndim != 1:
            raise ValueError("Pulse signal must be 1D numpy array")

        features = {}
        features.update(self.extract_time_domain_features(pulse))
        features.update(self.extract_frequency_domain_features(pulse))
        return features

    # ----------------------------------------------------
    # HELPERS
    # ----------------------------------------------------
    def _band_power(self, freqs, psd, band):
        mask = (freqs >= band[0]) & (freqs <= band[1])
        return float(np.trapz(psd[mask], freqs[mask])) if np.any(mask) else 0.0

    def _signal_to_noise_ratio(self, pulse: np.ndarray) -> float:
        signal_power = np.mean(pulse ** 2)
        noise = pulse - signal.medfilt(pulse, kernel_size=5)
        noise_power = np.mean(noise ** 2)
        return float(10 * np.log10(signal_power / noise_power)) if noise_power > 0 else 0.0

    def _baseline_wander(self, pulse: np.ndarray) -> float:
        baseline = signal.medfilt(pulse, kernel_size=self.sampling_rate)
        return float(np.std(pulse - baseline))
