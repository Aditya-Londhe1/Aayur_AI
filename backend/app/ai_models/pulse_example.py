"""
Example usage of pulse analysis system
"""

import numpy as np
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pulse_model import pulse_service
from pulse.pulse_features import PulseFeatureExtractor
from pulse.utils import visualize_pulse_waveform, create_analysis_report

def generate_sample_pulse(duration_seconds=10, sampling_rate=125, dosha_type='balanced'):
    """Generate sample pulse signal for testing"""
    t = np.arange(0, duration_seconds, 1/sampling_rate)
    
    # Base signal
    base_freq = 1.2  # ~72 BPM
    
    if dosha_type == 'vata':
        # Irregular, variable
        signal = np.sin(2 * np.pi * base_freq * t)
        signal += 0.3 * np.sin(2 * np.pi * 0.3 * t)  # Low frequency modulation
        signal += 0.1 * np.random.randn(len(t))  # Noise
        # Add some irregularity
        irregularity = np.zeros_like(t)
        irregular_indices = np.random.choice(len(t), size=50, replace=False)
        irregularity[irregular_indices] = 0.5 * np.random.randn(50)
        signal += irregularity
        
    elif dosha_type == 'pitta':
        # Strong, sharp peaks
        signal = np.sin(2 * np.pi * base_freq * t)
        signal = np.sign(signal) * np.abs(signal)**0.7  # Sharper peaks
        signal += 0.2 * np.sin(2 * np.pi * 0.5 * t)  # Harmonic
        signal *= 1.5  # Stronger amplitude
        
    elif dosha_type == 'kapha':
        # Slow, smooth
        signal = np.sin(2 * np.pi * 0.8 * t)  # Slower frequency
        signal += 0.1 * np.sin(2 * np.pi * 0.2 * t)  # Very slow modulation
        signal = np.convolve(signal, np.ones(10)/10, mode='same')  # Smooth
        
    else:  # balanced
        signal = np.sin(2 * np.pi * base_freq * t)
        signal += 0.1 * np.sin(2 * np.pi * 0.4 * t)  # Mild modulation
        signal += 0.05 * np.random.randn(len(t))  # Small noise
    
    # Normalize
    signal = (signal - np.mean(signal)) / np.std(signal)
    
    return signal

def example_single_analysis():
    """Example: Analyze a single pulse signal"""
    print("=" * 60)
    print("EXAMPLE: SINGLE PULSE ANALYSIS")
    print("=" * 60)
    
    # Generate sample pulse signal
    sample_signal = generate_sample_pulse(duration_seconds=8, dosha_type='vata')
    
    print(f"Generated pulse signal: {len(sample_signal)} samples")
    print(f"Duration: {len(sample_signal)/125:.1f} seconds")
    
    # Analyze the signal
    print("\nAnalyzing pulse...")
    results = pulse_service.analyze(sample_signal, sampling_rate=125)
    
    if 'error' in results and results['error']:
        print(f"Error: {results['errors']}")
        return
    
    # Print key results
    print("\nANALYSIS RESULTS:")
    print(f"Dominant Dosha: {results['prediction']['ayurvedic_dosha'].upper()}")
    print(f"Confidence: {results['prediction']['confidence']*100:.1f}%")
    
    print("\nDosha Scores:")
    for dosha, score in results['prediction']['dosha_scores'].items():
        print(f"  {dosha.upper():10}: {score*100:5.1f}%")
    
    print("\nPulse Characteristics:")
    for char, value in results['prediction']['characteristics'].items():
        print(f"  {char.replace('_', ' ').title():15}: {value}")
    
    print("\nHeart Rate:", results['signal_statistics'].get('heart_rate', 'N/A'), "bpm")
    
    # Generate full report
    report = create_analysis_report(results)
    print("\n" + "=" * 60)
    print("COMPLETE REPORT:")
    print("=" * 60)
    print(report)
    
    # Visualize
    print("\nGenerating visualization...")
    visualize_pulse_waveform(sample_signal, sampling_rate=125)
    
    return results

def example_batch_analysis():
    """Example: Analyze multiple pulse signals"""
    print("\n" + "=" * 60)
    print("EXAMPLE: BATCH ANALYSIS")
    print("=" * 60)
    
    # Generate multiple sample signals
    signals = []
    dosha_types = ['vata', 'pitta', 'kapha', 'balanced', 'vata']
    
    for i, dosha_type in enumerate(dosha_types):
        signal = generate_sample_pulse(duration_seconds=6, dosha_type=dosha_type)
        signals.append(signal)
        print(f"Signal {i+1}: {len(signal)} samples, Type: {dosha_type}")
    
    # Analyze batch
    print("\nAnalyzing batch...")
    batch_results = pulse_service.analyze_batch(signals, sampling_rate=125)
    
    print(f"\nBATCH STATISTICS:")
    stats = batch_results['batch_statistics']
    print(f"Total signals: {stats['total_signals']}")
    print(f"Valid signals: {stats['valid_signals']}")
    print(f"Completion rate: {stats['completion_rate']*100:.1f}%")
    
    print("\nINDIVIDUAL RESULTS:")
    for i, result in enumerate(batch_results['batch_analysis'][:3]):  # Show first 3
        if 'analysis' in result:
            pred = result['analysis']['prediction']
            print(f"Signal {i+1}: {pred['ayurvedic_dosha'].upper()} "
                  f"({pred['confidence']*100:.1f}%)")
    
    return batch_results

def example_feature_extraction():
    """Example: Extract features from pulse signal"""
    print("\n" + "=" * 60)
    print("EXAMPLE: FEATURE EXTRACTION")
    print("=" * 60)
    
    # Generate sample signal
    signal = generate_sample_pulse(duration_seconds=10)
    
    # Extract features
    extractor = PulseFeatureExtractor(sampling_rate=125)
    features = extractor.extract_all_features(signal)
    
    print(f"Extracted {len(features)} features")
    
    # Show some key features
    print("\nKEY FEATURES:")
    key_features = [
        'heart_rate', 'hrv', 'mean_rr', 'rmssd',
        'lf_power', 'hf_power', 'lf_hf_ratio',
        'sample_entropy', 'dfa_alpha'
    ]
    
    for key in key_features:
        if key in features:
            print(f"  {key:20}: {features[key]:.4f}")
    
    # Ayurvedic specific features
    print("\nAYURVEDIC FEATURES:")
    ayur_features = ['vata_score', 'pitta_score', 'kapha_score', 'rhythm_type', 'nadi_type']
    for key in ayur_features:
        if key in features:
            print(f"  {key:20}: {features[key]}")

def example_service_info():
    """Example: Get service information"""
    print("\n" + "=" * 60)
    print("EXAMPLE: SERVICE INFORMATION")
    print("=" * 60)
    
    info = pulse_service.get_service_info()
    
    print("Service Info:")
    for key, value in info.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for k, v in value.items():
                print(f"    {k}: {v}")
        else:
            print(f"  {key}: {value}")

def main():
    """Run all examples"""
    print("PULSE ANALYSIS SYSTEM - NADI PARIKSHA")
    print("Version 1.0.0")
    print("-" * 60)
    
    # Get service info
    example_service_info()
    
    # Single analysis
    results_single = example_single_analysis()
    
    # Batch analysis
    results_batch = example_batch_analysis()
    
    # Feature extraction
    example_feature_extraction()
    
    print("\n" + "=" * 60)
    print("EXAMPLES COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    
    # Save example results
    if results_single and 'error' not in results_single:
        from pulse.utils import save_analysis_results
        save_analysis_results(results_single, './example_pulse_analysis.json')
        print("\nSaved single analysis to: ./example_pulse_analysis.json")

if __name__ == '__main__':
    main()