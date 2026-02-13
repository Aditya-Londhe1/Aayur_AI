"""
Utility functions for pulse analysis system
"""

import numpy as np
import torch
import json
import yaml
import pickle
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def validate_pulse_signal(signal: np.ndarray, 
                         sampling_rate: int = 125,
                         min_length: int = 500) -> Dict[str, Any]:
    """
    Validate pulse signal quality
    
    Returns:
        Dictionary with validation results
    """
    results = {
        'is_valid': True,
        'issues': [],
        'quality_score': 1.0,
        'signal_statistics': {}
    }
    
    # Check signal length
    if len(signal) < min_length:
        results['is_valid'] = False
        results['issues'].append(f"Signal too short: {len(signal)} < {min_length}")
    
    # Check for NaN or Inf values
    if np.any(np.isnan(signal)) or np.any(np.isinf(signal)):
        results['is_valid'] = False
        results['issues'].append("Signal contains NaN or Inf values")
    
    # Check amplitude range
    signal_range = np.ptp(signal)
    if signal_range < 0.1:
        results['is_valid'] = False
        results['issues'].append(f"Signal amplitude too small: {signal_range}")
    
    # Check for flat signal
    if np.std(signal) < 0.01:
        results['is_valid'] = False
        results['issues'].append("Signal is too flat (low variance)")
    
    # Calculate quality metrics
    quality_factors = []
    
    # Signal-to-noise ratio estimation
    from scipy import signal as sp_signal
    filtered = sp_signal.medfilt(signal, kernel_size=5)
    noise = signal - filtered
    snr = np.var(signal) / (np.var(noise) + 1e-8)
    quality_factors.append(min(snr / 10, 1.0))
    
    # Dynamic range
    dynamic_range = np.log10(np.ptp(signal) / (np.std(noise) + 1e-8))
    quality_factors.append(min(dynamic_range / 2, 1.0))
    
    # Peak detection reliability
    peaks, _ = sp_signal.find_peaks(signal, 
                                   height=np.mean(signal) + np.std(signal),
                                   distance=sampling_rate // 4)
    
    if len(peaks) >= 2:
        # Check peak regularity
        peak_intervals = np.diff(peaks)
        cv = np.std(peak_intervals) / np.mean(peak_intervals)
        regularity_score = max(0, 1 - cv)
        quality_factors.append(regularity_score)
    else:
        quality_factors.append(0.1)
    
    # Calculate overall quality score
    if quality_factors:
        results['quality_score'] = float(np.mean(quality_factors))
    
    # Add signal statistics
    results['signal_statistics'] = {
        'length': len(signal),
        'mean': float(np.mean(signal)),
        'std': float(np.std(signal)),
        'min': float(np.min(signal)),
        'max': float(np.max(signal)),
        'range': float(np.ptp(signal)),
        'num_peaks': len(peaks),
        'sampling_rate': sampling_rate,
        'duration_seconds': len(signal) / sampling_rate
    }
    
    # Final validation
    if results['quality_score'] < 0.3:
        results['is_valid'] = False
        results['issues'].append(f"Low quality score: {results['quality_score']:.2f}")
    
    return results

def preprocess_pulse_signal(signal: np.ndarray,
                           sampling_rate: int = 125,
                           target_length: int = 1000) -> np.ndarray:
    """
    Preprocess pulse signal for analysis
    """
    from scipy import signal as sp_signal
    
    # 1. Remove baseline wander
    baseline = sp_signal.medfilt(signal, kernel_size=sampling_rate)
    signal_clean = signal - baseline
    
    # 2. Bandpass filter (0.5-5 Hz for pulse)
    nyquist = 0.5 * sampling_rate
    low = 0.5 / nyquist
    high = 5.0 / nyquist
    
    b, a = sp_signal.butter(4, [low, high], btype='band')
    signal_filtered = sp_signal.filtfilt(b, a, signal_clean)
    
    # 3. Normalize
    signal_normalized = (signal_filtered - np.mean(signal_filtered)) / np.std(signal_filtered)
    
    # 4. Resample if needed
    if len(signal_normalized) != target_length:
        if len(signal_normalized) > target_length:
            # Truncate
            signal_processed = signal_normalized[:target_length]
        else:
            # Pad with zeros
            pad_length = target_length - len(signal_normalized)
            signal_processed = np.pad(signal_normalized, (0, pad_length), mode='constant')
    else:
        signal_processed = signal_normalized
    
    return signal_processed

def save_analysis_results(results: Dict[str, Any], 
                         filepath: str,
                         format: str = 'json'):
    """
    Save analysis results to file
    """
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    
    # Add metadata
    results_with_meta = results.copy()
    results_with_meta['metadata'] = {
        'saved_at': datetime.now().isoformat(),
        'format': format,
        'version': '1.0.0'
    }
    
    if format.lower() == 'json':
        with open(filepath, 'w') as f:
            json.dump(results_with_meta, f, indent=2, default=str)
    
    elif format.lower() == 'yaml':
        with open(filepath, 'w') as f:
            yaml.dump(results_with_meta, f, default_flow_style=False)
    
    elif format.lower() == 'pickle':
        with open(filepath, 'wb') as f:
            pickle.dump(results_with_meta, f)
    
    else:
        raise ValueError(f"Unsupported format: {format}")
    
    logger.info(f"Results saved to {filepath}")
    return filepath

def load_analysis_results(filepath: str) -> Dict[str, Any]:
    """
    Load analysis results from file
    """
    if not Path(filepath).exists():
        raise FileNotFoundError(f"Results file not found: {filepath}")
    
    file_extension = Path(filepath).suffix.lower()
    
    if file_extension == '.json':
        with open(filepath, 'r') as f:
            results = json.load(f)
    
    elif file_extension in ['.yaml', '.yml']:
        with open(filepath, 'r') as f:
            results = yaml.safe_load(f)
    
    elif file_extension == '.pickle':
        with open(filepath, 'rb') as f:
            results = pickle.load(f)
    
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")
    
    return results

def calculate_signal_hash(signal: np.ndarray) -> str:
    """
    Calculate hash of signal for identification
    """
    # Convert signal to bytes
    signal_bytes = signal.tobytes()
    
    # Calculate hash
    hash_obj = hashlib.sha256(signal_bytes)
    return hash_obj.hexdigest()[:16]

def create_analysis_report(results: Dict[str, Any]) -> str:
    """
    Create human-readable analysis report
    """
    report = []
    
    report.append("=" * 60)
    report.append("PULSE ANALYSIS REPORT (NADI PARIKSHA)")
    report.append("=" * 60)
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # Dominant dosha
    dominant_dosha = results.get('dominant_dosha', 'unknown').upper()
    confidence = results.get('confidence', 0) * 100
    
    report.append(f"DOMINANT DOSHA: {dominant_dosha}")
    report.append(f"Confidence: {confidence:.1f}%")
    report.append("")
    
    # Dosha scores
    dosha_scores = results.get('dosha_scores', {})
    if dosha_scores:
        report.append("DOSHA DISTRIBUTION:")
        for dosha, score in dosha_scores.items():
            bar_length = int(score * 40)
            bar = '█' * bar_length + '░' * (40 - bar_length)
            report.append(f"  {dosha.upper():10} [{bar}] {score*100:5.1f}%")
        report.append("")
    
    # Characteristics
    characteristics = results.get('characteristics', {})
    if characteristics:
        report.append("PULSE CHARACTERISTICS:")
        for key, value in characteristics.items():
            report.append(f"  {key.replace('_', ' ').title():15}: {value}")
        report.append("")
    
    # Health indicators
    signal_stats = results.get('signal_statistics', {})
    if signal_stats:
        report.append("HEALTH INDICATORS:")
        hr = signal_stats.get('heart_rate', 0)
        if hr > 0:
            report.append(f"  Heart Rate: {hr:.0f} bpm")
            
            if hr < 60:
                report.append(f"    Interpretation: Bradycardia range (consult professional)")
            elif hr > 100:
                report.append(f"    Interpretation: Tachycardia range (consult professional)")
            else:
                report.append(f"    Interpretation: Normal range")
        
        hrv = results.get('features', {}).get('hrv', 0)
        if hrv > 0:
            report.append(f"  Heart Rate Variability: {hrv:.1f}%")
            
            if hrv > 20:
                report.append(f"    Interpretation: High variability (Vata influence)")
            elif hrv < 10:
                report.append(f"    Interpretation: Low variability (Kapha influence)")
            else:
                report.append(f"    Interpretation: Moderate variability")
        
        report.append("")
    
    # Recommendations
    recommendations = results.get('recommendations', {})
    if recommendations:
        report.append("AYURVEDIC RECOMMENDATIONS:")
        
        for category, items in recommendations.items():
            if items and isinstance(items, list):
                report.append(f"  {category.upper()}:")
                for item in items[:3]:  # Show top 3
                    report.append(f"    • {item}")
                report.append("")
    
    # Interpretation
    interpretation = results.get('interpretation', '')
    if interpretation:
        report.append("AYURVEDIC INTERPRETATION:")
        report.append(f"  {interpretation}")
        report.append("")
    
    # Disclaimer
    report.append("=" * 60)
    report.append("DISCLAIMER:")
    report.append("This analysis is for wellness guidance only, not medical diagnosis.")
    report.append("Consult healthcare professionals for medical concerns.")
    report.append("=" * 60)
    
    return "\n".join(report)

def visualize_pulse_waveform(signal: np.ndarray, 
                            sampling_rate: int = 125,
                            save_path: Optional[str] = None):
    """
    Visualize pulse waveform with annotations
    """
    import matplotlib.pyplot as plt
    from scipy import signal as sp_signal
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Time domain plot
    time = np.arange(len(signal)) / sampling_rate
    axes[0, 0].plot(time, signal, 'b-', linewidth=1)
    axes[0, 0].set_xlabel('Time (seconds)')
    axes[0, 0].set_ylabel('Amplitude')
    axes[0, 0].set_title('Pulse Waveform (Time Domain)')
    axes[0, 0].grid(True, alpha=0.3)
    
    # Detect and mark peaks
    peaks, properties = sp_signal.find_peaks(
        signal, 
        height=np.mean(signal) + np.std(signal),
        distance=sampling_rate // 4
    )
    
    if len(peaks) > 0:
        axes[0, 0].plot(time[peaks], signal[peaks], 'ro', markersize=5, label='Peaks')
        axes[0, 0].legend()
    
    # Frequency domain plot
    freqs, psd = sp_signal.welch(signal, fs=sampling_rate, nperseg=256)
    axes[0, 1].semilogy(freqs, psd, 'g-', linewidth=1)
    axes[0, 1].set_xlabel('Frequency (Hz)')
    axes[0, 1].set_ylabel('Power Spectral Density')
    axes[0, 1].set_title('Frequency Spectrum')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Mark Ayurvedic frequency bands
    vlf_band = (0.003, 0.04)  # Kapha
    lf_band = (0.04, 0.15)    # Pitta
    hf_band = (0.15, 0.4)     # Vata
    
    axes[0, 1].axvspan(*vlf_band, alpha=0.2, color='blue', label='Kapha (VLF)')
    axes[0, 1].axvspan(*lf_band, alpha=0.2, color='red', label='Pitta (LF)')
    axes[0, 1].axvspan(*hf_band, alpha=0.2, color='green', label='Vata (HF)')
    axes[0, 1].legend()
    
    # Poincaré plot (HRV)
    if len(peaks) > 2:
        rr_intervals = np.diff(peaks) / sampling_rate * 1000  # ms
        
        axes[1, 0].plot(rr_intervals[:-1], rr_intervals[1:], 'bo', alpha=0.5, markersize=3)
        axes[1, 0].plot([rr_intervals.min(), rr_intervals.max()], 
                       [rr_intervals.min(), rr_intervals.max()], 'r--', linewidth=1)
        axes[1, 0].set_xlabel('RR_n (ms)')
        axes[1, 0].set_ylabel('RR_{n+1} (ms)')
        axes[1, 0].set_title('Poincaré Plot (Heart Rate Variability)')
        axes[1, 0].grid(True, alpha=0.3)
    
    # Signal quality metrics
    axes[1, 1].axis('off')
    
    validation = validate_pulse_signal(signal, sampling_rate)
    stats = validation['signal_statistics']
    
    metrics_text = (
        f"Signal Quality Score: {validation['quality_score']:.2%}\n"
        f"Duration: {stats['duration_seconds']:.1f} seconds\n"
        f"Sampling Rate: {sampling_rate} Hz\n"
        f"Mean Amplitude: {stats['mean']:.3f}\n"
        f"Standard Deviation: {stats['std']:.3f}\n"
        f"Peak Count: {stats['num_peaks']}\n"
        f"Heart Rate: {stats.get('heart_rate', 'N/A')} bpm\n"
    )
    
    if validation['issues']:
        metrics_text += "\nIssues:\n"
        for issue in validation['issues'][:3]:
            metrics_text += f"• {issue}\n"
    
    axes[1, 1].text(0.1, 0.9, metrics_text, transform=axes[1, 1].transAxes,
                   fontfamily='monospace', verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.suptitle('Pulse Analysis Visualization', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Visualization saved to {save_path}")
    
    plt.show()
    return fig

def export_to_csv(results: Dict[str, Any], filepath: str):
    """
    Export analysis results to CSV format
    """
    import pandas as pd
    
    # Flatten nested dictionaries
    flat_data = {}
    
    def flatten_dict(d, prefix=''):
        for key, value in d.items():
            if isinstance(value, dict):
                flatten_dict(value, f"{prefix}{key}_")
            elif isinstance(value, list):
                # Convert list to string
                flat_data[f"{prefix}{key}"] = str(value)
            else:
                flat_data[f"{prefix}{key}"] = value
    
    flatten_dict(results)
    
    # Create DataFrame
    df = pd.DataFrame([flat_data])
    
    # Save to CSV
    df.to_csv(filepath, index=False)
    logger.info(f"Results exported to CSV: {filepath}")
    
    return filepath

class PulseAnalysisCache:
    """Cache for pulse analysis results"""
    
    def __init__(self, cache_dir: str = './cache/pulse_analysis'):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get_cache_key(self, signal: np.ndarray, analysis_type: str) -> str:
        """Generate cache key from signal"""
        signal_hash = calculate_signal_hash(signal)
        return f"{analysis_type}_{signal_hash}"
    
    def get(self, signal: np.ndarray, analysis_type: str) -> Optional[Dict]:
        """Get cached analysis results"""
        cache_key = self.get_cache_key(signal, analysis_type)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
        
        return None
    
    def set(self, signal: np.ndarray, analysis_type: str, results: Dict):
        """Cache analysis results"""
        cache_key = self.get_cache_key(signal, analysis_type)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(results, f, indent=2)
            logger.debug(f"Cached analysis: {cache_key}")
        except Exception as e:
            logger.warning(f"Failed to cache results: {e}")
    
    def clear_old_cache(self, max_age_days: int = 7):
        """Clear cache older than specified days"""
        cutoff_time = datetime.now().timestamp() - (max_age_days * 24 * 3600)
        
        for cache_file in self.cache_dir.glob('*.json'):
            if cache_file.stat().st_mtime < cutoff_time:
                try:
                    cache_file.unlink()
                    logger.debug(f"Cleared old cache: {cache_file.name}")
                except Exception as e:
                    logger.warning(f"Failed to clear cache file: {e}")