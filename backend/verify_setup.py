#!/usr/bin/env python3
"""
Quick Setup Verification Script
Checks if all required packages are installed
"""

import sys

print("=" * 60)
print("Voice Assistant Setup Verification")
print("=" * 60)

# Check Python version
print(f"\n✅ Python version: {sys.version.split()[0]}")

# Required packages
required_packages = {
    'google.generativeai': 'google-generativeai',
    'deep_translator': 'deep-translator',
    'langdetect': 'langdetect',
    'gtts': 'gtts',
    'pydub': 'pydub',
    'speech_recognition': 'SpeechRecognition',
    'dotenv': 'python-dotenv',
}

missing_packages = []
installed_packages = []

print("\nChecking required packages:")
print("-" * 60)

for module_name, package_name in required_packages.items():
    try:
        __import__(module_name)
        print(f"✅ {package_name}")
        installed_packages.append(package_name)
    except ImportError:
        print(f"❌ {package_name} - NOT INSTALLED")
        missing_packages.append(package_name)

# Check .env file
print("\n" + "-" * 60)
print("Checking configuration:")
print("-" * 60)

try:
    with open('.env', 'r') as f:
        env_content = f.read()
        if 'GEMINI_API_KEY' in env_content:
            print("✅ .env file exists with GEMINI_API_KEY")
        else:
            print("⚠️  .env file exists but GEMINI_API_KEY not found")
except FileNotFoundError:
    print("❌ .env file not found")

# Summary
print("\n" + "=" * 60)
print("Summary")
print("=" * 60)

if missing_packages:
    print(f"\n❌ Missing {len(missing_packages)} package(s):")
    for pkg in missing_packages:
        print(f"   - {pkg}")
    print("\nInstall missing packages:")
    print(f"pip install {' '.join(missing_packages)}")
    sys.exit(1)
else:
    print(f"\n✅ All {len(installed_packages)} required packages installed!")
    print("\nNext steps:")
    print("1. Run: python test_gemini.py")
    print("2. Run: python test_translation.py")
    print("3. Proceed to Option B implementation")
    sys.exit(0)
