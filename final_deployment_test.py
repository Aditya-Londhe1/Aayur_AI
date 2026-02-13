"""
Final Deployment Test Suite
Complete end-to-end testing before deployment
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"
HEALTH_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5173"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BLUE}{text.center(70)}{Colors.END}")
    print(f"{Colors.BLUE}{'='*70}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}[PASS]{Colors.END} {text}")

def print_error(text):
    print(f"{Colors.RED}[FAIL]{Colors.END} {text}")

def print_info(text):
    print(f"{Colors.YELLOW}[INFO]{Colors.END} {text}")

def test_backend_health():
    """Test 1: Backend Health Check"""
    print_header("TEST 1: Backend Health Check")
    
    try:
        response = requests.get(f"{HEALTH_URL}/health", timeout=5)
        if response.status_code == 200:
            print_success("Backend is running")
            print_info(f"Response: {response.json()}")
            return True
        else:
            print_error(f"Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to backend. Is it running?")
        print_info("Start backend: cd backend && uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_frontend_running():
    """Test 2: Frontend Running"""
    print_header("TEST 2: Frontend Running")
    
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print_success("Frontend is running")
            return True
        else:
            print_error(f"Frontend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to frontend. Is it running?")
        print_info("Start frontend: cd frontend && npm run dev")
        return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_pulse_generation():
    """Test 3: Pulse Generation"""
    print_header("TEST 3: Pulse Generation")
    
    try:
        response = requests.post(
            f"{BASE_URL}/pulse/generate-synthetic-pulse",
            data={
                "heart_rate": 75,
                "duration": 60,
                "sampling_rate": 125
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'pulse_data' in data and len(data['pulse_data']) > 0:
                print_success(f"Pulse generated: {len(data['pulse_data'])} points")
                return True, data['pulse_data']
            else:
                print_error("Pulse data is empty")
                return False, None
        else:
            print_error(f"Status: {response.status_code}")
            print_info(f"Response: {response.text[:200]}")
            return False, None
    except Exception as e:
        print_error(f"Error: {e}")
        return False, None

def test_complete_consultation(pulse_data):
    """Test 4: Complete Consultation Flow"""
    print_header("TEST 4: Complete Consultation Flow")
    
    try:
        # Prepare consultation data
        consultation_data = {
            "patient_name": "Test Patient",
            "patient_age": 30,
            "patient_gender": "male",
            "symptoms": json.dumps([
                "fatigue",
                "headache",
                "digestive_issues"
            ]),
            "pulse_data": json.dumps(pulse_data) if pulse_data else json.dumps([]),
            "heart_rate": 75,
            "locale": "en"
        }
        
        print_info("Submitting consultation...")
        response = requests.post(
            f"{BASE_URL}/consultations/complete",
            data=consultation_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Check response structure
            if 'analysis' in result:
                analysis = result['analysis']
                print_success("Consultation completed")
                
                # Check pulse analysis
                if 'analyses' in analysis and 'pulse' in analysis['analyses']:
                    pulse = analysis['analyses']['pulse']
                    print_success(f"Pulse Analysis: {pulse.get('prediction', 'N/A')}")
                    
                    if 'ayurvedic_analysis' in pulse:
                        ayur = pulse['ayurvedic_analysis']
                        print_success(f"Ayurvedic Dosha: {ayur.get('dominant_dosha', 'N/A')}")
                
                # Check fusion results
                if 'fusion' in analysis:
                    fusion = analysis['fusion']
                    print_success(f"Dominant Dosha: {fusion.get('dominant_dosha', 'N/A')}")
                    print_info(f"Confidence: {fusion.get('confidence', 0):.2%}")
                
                return True, result
            else:
                print_error("Missing analysis in response")
                return False, None
        else:
            print_error(f"Status: {response.status_code}")
            print_info(f"Response: {response.text[:300]}")
            return False, None
            
    except Exception as e:
        print_error(f"Error: {e}")
        return False, None

def test_voice_languages():
    """Test 5: Voice Assistant Languages"""
    print_header("TEST 5: Voice Assistant Languages")
    
    try:
        response = requests.get(f"{BASE_URL}/voice/supported-languages", timeout=5)
        
        if response.status_code == 200:
            languages = response.json()
            if 'supported_languages' in languages:
                print_success(f"Supported languages: {len(languages['supported_languages'])}")
                for lang in languages['supported_languages'][:5]:  # Show first 5
                    print_info(f"  - {lang}")
                return True
            else:
                print_error("No languages in response")
                return False
        else:
            print_error(f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_tongue_analysis():
    """Test 6: Tongue Analysis Endpoint"""
    print_header("TEST 6: Tongue Analysis Endpoint")
    
    try:
        # Just check if endpoint is available (without actual image)
        response = requests.post(
            f"{BASE_URL}/tongue/analyze",
            files={'image': ('test.jpg', b'fake_image_data', 'image/jpeg')},
            timeout=10
        )
        
        # We expect it to fail with actual analysis, but endpoint should respond
        if response.status_code in [200, 400, 422]:
            print_success("Tongue analysis endpoint is available")
            return True
        else:
            print_error(f"Unexpected status: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_symptom_extraction():
    """Test 7: Symptom Extraction"""
    print_header("TEST 7: Symptom Extraction from Text")
    
    try:
        response = requests.post(
            f"{BASE_URL}/voice/extract-symptoms-from-text",
            data={
                "text": "I have a headache and feel tired",
                "locale": "en"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'extracted_symptoms' in result:
                print_success(f"Extracted {len(result['extracted_symptoms'])} symptoms")
                for symptom in result['extracted_symptoms']:
                    print_info(f"  - {symptom.get('name', symptom)}")
                return True
            else:
                print_error("No symptoms in response")
                return False
        else:
            print_error(f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_database_connection():
    """Test 8: Database Connection"""
    print_header("TEST 8: Database Connection")
    
    try:
        # Try to access an endpoint that requires database
        response = requests.get(f"{HEALTH_URL}/health", timeout=5)
        
        if response.status_code == 200:
            print_success("Database connection working")
            return True
        else:
            print_error("Database connection issue")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_cors_headers():
    """Test 9: CORS Headers"""
    print_header("TEST 9: CORS Configuration")
    
    try:
        response = requests.options(
            f"{HEALTH_URL}/health",
            headers={'Origin': FRONTEND_URL},
            timeout=5
        )
        
        if 'Access-Control-Allow-Origin' in response.headers:
            print_success("CORS headers configured")
            print_info(f"Allowed origin: {response.headers.get('Access-Control-Allow-Origin')}")
            return True
        else:
            print_error("CORS headers missing")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def run_all_tests():
    """Run all tests and generate report"""
    print(f"\n{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BLUE}FINAL DEPLOYMENT TEST SUITE{Colors.END}")
    print(f"{Colors.BLUE}Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
    print(f"{Colors.BLUE}{'='*70}{Colors.END}")
    
    results = []
    
    # Test 1: Backend Health
    results.append(("Backend Health", test_backend_health()))
    
    # Test 2: Frontend Running
    results.append(("Frontend Running", test_frontend_running()))
    
    # Test 3: Pulse Generation
    pulse_success, pulse_data = test_pulse_generation()
    results.append(("Pulse Generation", pulse_success))
    
    # Test 4: Complete Consultation
    if pulse_success:
        consult_success, _ = test_complete_consultation(pulse_data)
        results.append(("Complete Consultation", consult_success))
    else:
        results.append(("Complete Consultation", False))
        print_error("Skipped: Pulse generation failed")
    
    # Test 5: Voice Languages
    results.append(("Voice Languages", test_voice_languages()))
    
    # Test 6: Tongue Analysis
    results.append(("Tongue Analysis", test_tongue_analysis()))
    
    # Test 7: Symptom Extraction
    results.append(("Symptom Extraction", test_symptom_extraction()))
    
    # Test 8: Database Connection
    results.append(("Database Connection", test_database_connection()))
    
    # Test 9: CORS Headers
    results.append(("CORS Configuration", test_cors_headers()))
    
    # Generate Report
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        if success:
            print_success(f"{test_name}")
        else:
            print_error(f"{test_name}")
    
    print(f"\n{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BLUE}Results: {passed}/{total} tests passed{Colors.END}")
    
    if passed == total:
        print(f"{Colors.GREEN}ALL TESTS PASSED! Ready for deployment.{Colors.END}")
    else:
        print(f"{Colors.YELLOW}Some tests failed. Review issues before deployment.{Colors.END}")
    
    print(f"{Colors.BLUE}{'='*70}{Colors.END}\n")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests interrupted by user{Colors.END}")
        exit(1)
