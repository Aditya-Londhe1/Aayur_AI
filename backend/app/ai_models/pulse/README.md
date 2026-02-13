# Pulse Analysis System - Nadi Pariksha

A deep learning system for Ayurvedic pulse analysis using Bi-LSTM neural networks.

## Overview

This system analyzes pulse waveforms (photoplethysmogram - PPG) to determine Ayurvedic dosha balance using advanced signal processing and deep learning techniques.

## Features

- **Bi-LSTM Model**: Temporal pattern recognition for pulse rhythm analysis
- **Ayurvedic Mapping**: Scientific correlation between pulse features and doshas
- **Feature Extraction**: Comprehensive time, frequency, and nonlinear features
- **Explainable AI**: Human-readable interpretations and visualizations
- **Batch Processing**: Efficient analysis of multiple signals
- **Caching**: Performance optimization with result caching

## Ayurvedic Interpretation

The system maps pulse characteristics to traditional Ayurvedic concepts:

| Dosha | Pulse Characteristics | Modern Signal Features |
|-------|----------------------|------------------------|
| **Vata** | Irregular, quick, serpentine | High HRV, irregular rhythm, complex entropy |
| **Pitta** | Strong, sharp, jumping | High amplitude, sharp peaks, elevated HR |
| **Kapha** | Slow, steady, swan-like | Low HR, stable rhythm, high low-frequency power |
| **Balanced** | Harmonious, rhythmic | Moderate features, good variability, stable rhythm |

## Installation

1. Install required packages:
```bash
pip install torch numpy scipy scikit-learn matplotlib seaborn wfdb pyyaml