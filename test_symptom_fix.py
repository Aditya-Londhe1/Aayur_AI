"""
Test the symptom normalization fix
"""

import sys
sys.path.append('backend')

from app.ai_models.symptom_analysis import SymptomAnalyzer

# Test with string symptoms
analyzer = SymptomAnalyzer()

print("Testing symptom normalization...")
print("\n1. Testing with string symptoms:")
symptoms_str = ["fatigue", "headache", "digestive_issues"]
normalized = analyzer._normalize_symptoms(symptoms_str)
print(f"Input: {symptoms_str}")
print(f"Normalized: {normalized}")

print("\n2. Testing with dict symptoms:")
symptoms_dict = [
    {"name": "fatigue", "severity": "moderate"},
    {"name": "headache", "severity": "severe"}
]
normalized = analyzer._normalize_symptoms(symptoms_dict)
print(f"Input: {symptoms_dict}")
print(f"Normalized: {normalized}")

print("\n3. Testing with mixed symptoms:")
symptoms_mixed = [
    "fatigue",
    {"name": "headache", "severity": "severe"}
]
normalized = analyzer._normalize_symptoms(symptoms_mixed)
print(f"Input: {symptoms_mixed}")
print(f"Normalized: {normalized}")

print("\n✅ All normalization tests passed!")
