import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import consultationService from '../services/consultationService';
import pulseService from '../services/pulseService';
import '../styles/animations.css';

const IncrementalConsultation = ({ language = 'en' }) => {
  const navigate = useNavigate();
  const [consultationId, setConsultationId] = useState(null);
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const [patientData, setPatientData] = useState({
    name: '',
    age: '',
    gender: 'female'
  });
  
  const [symptoms, setSymptoms] = useState([]);
  const [customSymptom, setCustomSymptom] = useState('');
  const [heartRate, setHeartRate] = useState(72);
  const [tongueImage, setTongueImage] = useState(null);
  const [tonguePreview, setTonguePreview] = useState(null);
  
  const fileInputRef = useRef(null);
  
  const commonSymptoms = [
    'Headache', 'Fatigue', 'Anxiety', 'Insomnia',
    'Acidity', 'Constipation', 'Diarrhea', 'Nausea',
    'Joint Pain', 'Back Pain', 'Muscle Ache', 'Weakness'
  ];
  
  const steps = [
    { number: 1, title: 'Patient Info', icon: '👤' },
    { number: 2, title: 'Symptoms', icon: '📋' },
    { number: 3, title: 'Pulse', icon: '💓' },
    { number: 4, title: 'Tongue', icon: '👅' },
    { number: 5, title: 'Review', icon: '✓' }
  ];
  
  // Step 1: Create consultation
  const handleCreateConsultation = async () => {
    // Validation
    if (!patientData.name || !patientData.name.trim()) {
      setError('Please enter patient name');
      return;
    }
    if (!patientData.age || patientData.age < 1 || patientData.age > 120) {
      setError('Please enter a valid age (1-120)');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const result = await consultationService.createConsultation(patientData);
      setConsultationId(result.consultation_id);
      setCurrentStep(2);
    } catch (err) {
      setError('Failed to create consultation. Please check your connection and try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  // Step 2: Add symptoms
  const handleAddSymptoms = async () => {
    if (symptoms.length === 0) {
      setError('Please select at least one symptom');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      await consultationService.addSymptoms(consultationId, symptoms);
      setCurrentStep(3);
    } catch (err) {
      setError('Failed to add symptoms. Please check your connection and try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  // Step 3: Add pulse
  const handleAddPulse = async () => {
    if (heartRate < 40 || heartRate > 200) {
      setError('Please set a valid heart rate (40-200 BPM)');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      // Generate synthetic pulse data
      const pulseResult = await pulseService.generateSyntheticPulse(heartRate, 30);
      
      if (pulseResult.success) {
        await consultationService.addPulseAnalysis(consultationId, pulseResult.pulse_data);
        setCurrentStep(4);
      } else {
        setError('Failed to generate pulse data. Please try again.');
      }
    } catch (err) {
      setError('Failed to add pulse analysis. Please check your connection and try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  // Step 4: Add tongue (optional)
  const handleAddTongue = async () => {
    setLoading(true);
    setError(null);
    
    try {
      if (tongueImage) {
        // Validate image file
        if (!tongueImage.type.startsWith('image/')) {
          setError('Please upload a valid image file');
          setLoading(false);
          return;
        }
        await consultationService.addTongueAnalysis(consultationId, tongueImage);
      }
      setCurrentStep(5);
    } catch (err) {
      setError('Failed to add tongue analysis. Please check your connection and try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  // Step 5: Generate report
  const handleGenerateReport = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await consultationService.generateReport(consultationId);
      
      if (result && result.analysis) {
        // Navigate to results page with the analysis
        navigate('/results', { 
          state: { 
            result: result.analysis,
            patientInfo: patientData
          } 
        });
      } else {
        setError('Report generated but no analysis data received. Please try again.');
      }
    } catch (err) {
      setError('Failed to generate report. Please check your connection and try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  const addSymptom = (symptomName) => {
    if (symptoms.find(s => s.name === symptomName)) return;
    setSymptoms([...symptoms, { name: symptomName, severity: 'moderate' }]);
  };
  
  const removeSymptom = (index) => {
    setSymptoms(symptoms.filter((_, i) => i !== index));
  };
  
  const handleTongueImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        setError('Please select a valid image file');
        return;
      }
      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        setError('Image file size must be less than 5MB');
        return;
      }
      setTongueImage(file);
      setTonguePreview(URL.createObjectURL(file));
      setError(null);
    }
  };
  
  return (
    <div style={styles.container} className="fade-in">
      <h2 style={styles.title} className="slide-in-down">Step-by-Step Consultation</h2>
      
      {/* Progress Steps */}
      <div style={styles.progressSteps} className="fade-in delay-100">
        {steps.map((step, index) => (
          <div 
            key={step.number}
            style={{
              ...styles.step,
              ...(currentStep >= step.number ? styles.stepActive : {}),
              ...(currentStep === step.number ? styles.stepCurrent : {})
            }}
            className={`${currentStep >= step.number ? 'step-active' : ''} ${currentStep === step.number ? 'scale-in' : ''} delay-${index}00`}
          >
            <div style={styles.stepIcon}>{step.icon}</div>
            <div style={styles.stepTitle}>{step.title}</div>
          </div>
        ))}
      </div>
      
      {error && (
        <div style={styles.error} className="error-shake slide-in-down">
          <span>⚠️</span>
          <span>{error}</span>
        </div>
      )}
      
      {/* Step Content */}
      <div style={styles.stepContent} className="slide-in-up">
        {currentStep === 1 && (
          <div style={styles.form} className="fade-in">
            <h3>Patient Information</h3>
            <div style={styles.formGroup} className="slide-in-left delay-100">
              <label>Name *</label>
              <input
                type="text"
                value={patientData.name}
                onChange={(e) => setPatientData({...patientData, name: e.target.value})}
                style={styles.input}
                placeholder="Enter patient name"
              />
            </div>
            <div style={styles.formGroup} className="slide-in-left delay-200">
              <label>Age *</label>
              <input
                type="number"
                value={patientData.age}
                onChange={(e) => setPatientData({...patientData, age: e.target.value})}
                style={styles.input}
                placeholder="Enter age"
                min="1"
                max="120"
              />
            </div>
            <div style={styles.formGroup}>
              <label>Gender *</label>
              <select
                value={patientData.gender}
                onChange={(e) => setPatientData({...patientData, gender: e.target.value})}
                style={styles.input}
              >
                <option value="female">Female</option>
                <option value="male">Male</option>
                <option value="other">Other</option>
              </select>
            </div>
            <button 
              onClick={handleCreateConsultation}
              disabled={loading}
              style={styles.button}
              className={loading ? 'pulse' : 'button-hover'}
            >
              {loading ? (
                <>
                  <span className="loading-dots">Creating</span>
                </>
              ) : (
                'Next: Add Symptoms →'
              )}
            </button>
          </div>
        )}
        
        {currentStep === 2 && (
          <div style={styles.form} className="fade-in">
            <h3>Symptoms</h3>
            <p style={styles.helpText}>Select or add symptoms you're experiencing</p>
            
            <div style={styles.symptomGrid}>
              {commonSymptoms.map((symptom, index) => (
                <button
                  key={symptom}
                  onClick={() => addSymptom(symptom)}
                  style={{
                    ...styles.symptomButton,
                    ...(symptoms.find(s => s.name === symptom) ? styles.symptomButtonActive : {})
                  }}
                  className={`button-hover scale-in delay-${Math.min(index, 5)}00`}
                  disabled={symptoms.find(s => s.name === symptom)}
                >
                  {symptom}
                </button>
              ))}
            </div>
            
            <div style={styles.customSymptom}>
              <input
                type="text"
                value={customSymptom}
                onChange={(e) => setCustomSymptom(e.target.value)}
                placeholder="Add custom symptom..."
                style={styles.input}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && customSymptom.trim()) {
                    addSymptom(customSymptom.trim());
                    setCustomSymptom('');
                  }
                }}
              />
              <button
                onClick={() => {
                  if (customSymptom.trim()) {
                    addSymptom(customSymptom.trim());
                    setCustomSymptom('');
                  }
                }}
                style={styles.addButton}
              >
                Add
              </button>
            </div>
            
            {symptoms.length > 0 && (
              <div style={styles.selectedSymptoms}>
                <h4>Selected Symptoms:</h4>
                {symptoms.map((symptom, index) => (
                  <div key={index} style={styles.symptomTag}>
                    <span>{symptom.name}</span>
                    <button onClick={() => removeSymptom(index)} style={styles.removeButton}>
                      ×
                    </button>
                  </div>
                ))}
              </div>
            )}
            
            <button 
              onClick={handleAddSymptoms}
              disabled={loading || symptoms.length === 0}
              style={styles.button}
            >
              {loading ? 'Adding...' : 'Next: Add Pulse →'}
            </button>
          </div>
        )}
        
        {currentStep === 3 && (
          <div style={styles.form}>
            <h3>Pulse Measurement</h3>
            <p style={styles.helpText}>Enter your heart rate (beats per minute)</p>
            
            <div style={styles.pulseInput}>
              <label>Heart Rate: {heartRate} BPM</label>
              <input
                type="range"
                min="40"
                max="200"
                value={heartRate}
                onChange={(e) => setHeartRate(parseInt(e.target.value))}
                style={styles.slider}
              />
              <div style={styles.pulseRange}>
                <span>40</span>
                <span>200</span>
              </div>
            </div>
            
            <button 
              onClick={handleAddPulse}
              disabled={loading}
              style={styles.button}
            >
              {loading ? 'Processing...' : 'Next: Add Tongue (Optional) →'}
            </button>
          </div>
        )}
        
        {currentStep === 4 && (
          <div style={styles.form}>
            <h3>Tongue Image (Optional)</h3>
            <p style={styles.helpText}>Upload a clear photo of your tongue</p>
            
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleTongueImageChange}
              style={{ display: 'none' }}
            />
            
            <button
              onClick={() => fileInputRef.current.click()}
              style={styles.uploadButton}
            >
              📷 {tongueImage ? 'Change Image' : 'Upload Image'}
            </button>
            
            {tonguePreview && (
              <div style={styles.imagePreview}>
                <img src={tonguePreview} alt="Tongue preview" style={styles.previewImage} />
              </div>
            )}
            
            <div style={styles.buttonGroup}>
              <button 
                onClick={() => {
                  setTongueImage(null);
                  setTonguePreview(null);
                  setCurrentStep(5);
                }}
                style={styles.skipButton}
              >
                Skip
              </button>
              <button 
                onClick={handleAddTongue}
                disabled={loading}
                style={styles.button}
              >
                {loading ? 'Processing...' : 'Next: Review →'}
              </button>
            </div>
          </div>
        )}
        
        {currentStep === 5 && (
          <div style={styles.form}>
            <h3>Review & Generate Report</h3>
            
            <div style={styles.review}>
              <div style={styles.reviewSection}>
                <h4>Patient Information</h4>
                <p>Name: {patientData.name}</p>
                <p>Age: {patientData.age}</p>
                <p>Gender: {patientData.gender}</p>
              </div>
              
              <div style={styles.reviewSection}>
                <h4>Symptoms ({symptoms.length})</h4>
                {symptoms.map((s, i) => (
                  <p key={i}>• {s.name}</p>
                ))}
              </div>
              
              <div style={styles.reviewSection}>
                <h4>Pulse</h4>
                <p>Heart Rate: {heartRate} BPM</p>
              </div>
              
              <div style={styles.reviewSection}>
                <h4>Tongue Image</h4>
                <p>{tongueImage ? '✓ Uploaded' : '✗ Not provided'}</p>
              </div>
            </div>
            
            <button 
              onClick={handleGenerateReport}
              disabled={loading}
              style={{...styles.button, ...styles.generateButton}}
              className={loading ? 'button-pulse' : 'button-hover scale-in'}
            >
              {loading ? (
                <>
                  <span className="spinner spinner-small" style={{borderTopColor: 'white', marginRight: '8px'}}></span>
                  <span>Generating Report...</span>
                </>
              ) : (
                '✓ Generate Report'
              )}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

const styles = {
  container: {
    maxWidth: '800px',
    margin: '0 auto',
    padding: '20px'
  },
  title: {
    textAlign: 'center',
    marginBottom: '30px',
    color: '#333'
  },
  progressSteps: {
    display: 'flex',
    justifyContent: 'space-between',
    marginBottom: '40px',
    position: 'relative'
  },
  step: {
    flex: 1,
    textAlign: 'center',
    opacity: 0.4,
    transition: 'all 0.3s'
  },
  stepActive: {
    opacity: 1
  },
  stepCurrent: {
    opacity: 1,
    transform: 'scale(1.1)'
  },
  stepIcon: {
    fontSize: '32px',
    marginBottom: '8px'
  },
  stepTitle: {
    fontSize: '12px',
    fontWeight: '500'
  },
  error: {
    padding: '12px',
    backgroundColor: '#ffebee',
    color: '#c62828',
    borderRadius: '8px',
    marginBottom: '20px',
    display: 'flex',
    alignItems: 'center',
    gap: '8px'
  },
  stepContent: {
    backgroundColor: 'white',
    padding: '30px',
    borderRadius: '12px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
  },
  form: {
    maxWidth: '600px',
    margin: '0 auto'
  },
  formGroup: {
    marginBottom: '20px'
  },
  input: {
    width: '100%',
    padding: '12px',
    fontSize: '14px',
    border: '1px solid #ddd',
    borderRadius: '6px',
    marginTop: '4px'
  },
  button: {
    width: '100%',
    padding: '14px',
    fontSize: '16px',
    fontWeight: '500',
    backgroundColor: '#4CAF50',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    marginTop: '20px'
  },
  helpText: {
    color: '#666',
    fontSize: '14px',
    marginBottom: '16px'
  },
  symptomGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(140px, 1fr))',
    gap: '10px',
    marginBottom: '20px'
  },
  symptomButton: {
    padding: '10px',
    fontSize: '13px',
    border: '1px solid #ddd',
    borderRadius: '6px',
    backgroundColor: 'white',
    cursor: 'pointer',
    transition: 'all 0.2s'
  },
  symptomButtonActive: {
    backgroundColor: '#4CAF50',
    color: 'white',
    borderColor: '#4CAF50'
  },
  customSymptom: {
    display: 'flex',
    gap: '10px',
    marginBottom: '20px'
  },
  addButton: {
    padding: '12px 24px',
    fontSize: '14px',
    backgroundColor: '#2196F3',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer'
  },
  selectedSymptoms: {
    marginTop: '20px'
  },
  symptomTag: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '8px',
    padding: '8px 12px',
    backgroundColor: '#e3f2fd',
    borderRadius: '20px',
    margin: '4px',
    fontSize: '14px'
  },
  removeButton: {
    background: 'none',
    border: 'none',
    fontSize: '20px',
    cursor: 'pointer',
    color: '#666'
  },
  pulseInput: {
    marginBottom: '20px'
  },
  slider: {
    width: '100%',
    marginTop: '10px'
  },
  pulseRange: {
    display: 'flex',
    justifyContent: 'space-between',
    fontSize: '12px',
    color: '#666',
    marginTop: '4px'
  },
  uploadButton: {
    padding: '14px 24px',
    fontSize: '16px',
    backgroundColor: '#2196F3',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    marginBottom: '20px'
  },
  imagePreview: {
    textAlign: 'center',
    marginBottom: '20px'
  },
  previewImage: {
    maxWidth: '300px',
    maxHeight: '300px',
    borderRadius: '8px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
  },
  buttonGroup: {
    display: 'flex',
    gap: '12px'
  },
  skipButton: {
    flex: 1,
    padding: '14px',
    fontSize: '16px',
    backgroundColor: '#f5f5f5',
    color: '#333',
    border: '1px solid #ddd',
    borderRadius: '8px',
    cursor: 'pointer'
  },
  review: {
    marginBottom: '20px'
  },
  reviewSection: {
    marginBottom: '20px',
    padding: '16px',
    backgroundColor: '#f9f9f9',
    borderRadius: '8px'
  },
  generateButton: {
    backgroundColor: '#FF9800',
    fontSize: '18px'
  }
};

export default IncrementalConsultation;
