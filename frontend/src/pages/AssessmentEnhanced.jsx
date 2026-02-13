import React, { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import VoiceAssessment from '../components/VoiceAssessment'
import { t } from '../i18n/translations'

const API_URL = 'http://localhost:8000/api/v1'

function AssessmentEnhanced({ language }) {
  const navigate = useNavigate()
  const [assessmentMode, setAssessmentMode] = useState(null) // 'manual' or 'voice'
  const [currentStep, setCurrentStep] = useState(1)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // Form data state
  const [formData, setFormData] = useState({
    name: '',
    age: '',
    gender: 'female',
    weight: '',
    height: '',
    symptoms: [],
    customSymptom: '',
    heartRate: 72,
    pulseData: null,
    tongueImage: null,
    tonguePreview: null,
    voiceAudio: null,
    voicePreview: null,
    voiceTranscript: ''
  })

  const fileInputRef = useRef(null)
  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])

  const totalSteps = 5

  // Common symptoms for quick selection
  const commonSymptoms = [
    'Headache', 'Fatigue', 'Anxiety', 'Insomnia',
    'Acidity', 'Constipation', 'Diarrhea', 'Nausea',
    'Joint Pain', 'Back Pain', 'Muscle Ache', 'Weakness',
    'Dry Skin', 'Oily Skin', 'Skin Rash', 'Itching',
    'Cough', 'Cold', 'Fever', 'Sore Throat'
  ]

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const validateStep1 = () => {
    if (!formData.name.trim()) {
      setError(t('error.name_required', language) || 'Please enter your name')
      return false
    }
    if (!formData.age || formData.age < 1 || formData.age > 120) {
      setError(t('error.age_invalid', language) || 'Please enter a valid age')
      return false
    }
    return true
  }

  const addSymptom = (symptomName) => {
    if (formData.symptoms.find(s => s.name.toLowerCase() === symptomName.toLowerCase())) {
      return
    }
    setFormData(prev => ({
      ...prev,
      symptoms: [...prev.symptoms, { name: symptomName, severity: 'moderate' }]
    }))
  }

  const addCustomSymptom = () => {
    if (formData.customSymptom.trim()) {
      addSymptom(formData.customSymptom.trim())
      setFormData(prev => ({ ...prev, customSymptom: '' }))
    }
  }

  const removeSymptom = (index) => {
    setFormData(prev => ({
      ...prev,
      symptoms: prev.symptoms.filter((_, i) => i !== index)
    }))
  }

  const updateSymptomSeverity = (index, severity) => {
    setFormData(prev => ({
      ...prev,
      symptoms: prev.symptoms.map((s, i) => 
        i === index ? { ...s, severity } : s
      )
    }))
  }

  const handleHeartRateChange = async (e) => {
    const hr = parseInt(e.target.value)
    setFormData(prev => ({
      ...prev,
      heartRate: hr
    }))
    
    // Generate pulse data from backend
    try {
      const response = await fetch(`${API_URL}/pulse/generate-synthetic-pulse`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          heart_rate: hr.toString(),
          duration: '60',
          sampling_rate: '50'
        })
      })
      
      if (response.ok) {
        const result = await response.json()
        if (result.success) {
          setFormData(prev => ({
            ...prev,
            pulseData: result.pulse_data
          }))
        }
      }
    } catch (error) {
      console.error('Failed to generate pulse data:', error)
      // Fallback: keep previous pulse data or set to null
    }
  }

  const handleTongueImageChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      if (!file.type.startsWith('image/')) {
        setError('Please upload an image file')
        return
      }
      if (file.size > 5 * 1024 * 1024) {
        setError('Image size should be less than 5MB')
        return
      }
      setFormData(prev => ({
        ...prev,
        tongueImage: file,
        tonguePreview: URL.createObjectURL(file)
      }))
      setError(null)
    }
  }

  const removeTongueImage = () => {
    setFormData(prev => ({
      ...prev,
      tongueImage: null,
      tonguePreview: null
    }))
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleVoiceComplete = (voiceData) => {
    console.log('Voice complete, data:', voiceData)
    
    // Add symptoms from voice
    if (voiceData.symptoms && voiceData.symptoms.length > 0) {
      voiceData.symptoms.forEach(symptom => {
        addSymptom(symptom.name || symptom)
      })
    }
    
    setFormData(prev => ({
      ...prev,
      voiceTranscript: voiceData.transcript
    }))
    
    // Switch to manual mode and start from beginning
    // User will see their symptoms already added in step 2
    setAssessmentMode('manual')
    setCurrentStep(1)  // Start at basic info
  }

  const handleNext = () => {
    setError(null)
    
    if (currentStep === 1 && !validateStep1()) {
      return
    }
    
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1)
    } else {
      handleSubmit()
    }
  }

  const handleBack = () => {
    setError(null)
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
    }
  }

  const handleSubmit = async () => {
    setLoading(true)
    setError(null)

    try {
      const apiFormData = new FormData()
      apiFormData.append('patient_name', formData.name)
      apiFormData.append('patient_age', formData.age)
      apiFormData.append('patient_gender', formData.gender)
      
      if (formData.symptoms.length > 0) {
        apiFormData.append('symptoms', JSON.stringify(formData.symptoms))
      }
      
      if (formData.pulseData) {
        apiFormData.append('pulse_data', JSON.stringify(formData.pulseData))
        apiFormData.append('heart_rate', formData.heartRate) // Send the actual BPM value
      }
      
      if (formData.tongueImage) {
        apiFormData.append('tongue_image', formData.tongueImage)
      }
      
      apiFormData.append('locale', language || 'en')

      const response = await fetch(`${API_URL}/consultations/complete`, {
        method: 'POST',
        body: apiFormData
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Analysis failed')
      }

      const result = await response.json()
      
      navigate('/results', { state: { result: result.analysis, patientInfo: formData } })
      
    } catch (err) {
      setError(err.message || 'Failed to complete assessment. Please try again.')
      console.error('Assessment error:', err)
    } finally {
      setLoading(false)
    }
  }

  // Mode selection screen
  if (!assessmentMode) {
    return (
      <div className="assessment-container">
        <div className="mode-selection">
          <h1>{t('assessment.choose_mode', language) || 'Choose Assessment Mode'}</h1>
          <p className="mode-subtitle">
            {t('assessment.mode_subtitle', language) || 'Select how you would like to provide your health information'}
          </p>
          
          <div className="mode-cards">
            <div className="mode-card" onClick={() => setAssessmentMode('voice')}>
              <div className="mode-icon">🎤</div>
              <h2>{t('assessment.voice_mode', language) || 'Voice Mode'}</h2>
              <p>{t('assessment.voice_desc', language) || 'Speak your symptoms naturally - perfect for rural areas and those who prefer speaking'}</p>
              <div className="mode-features">
                <span className="feature-badge">✓ Easy & Natural</span>
                <span className="feature-badge">✓ Multi-language</span>
                <span className="feature-badge">✓ Hands-free</span>
              </div>
              <button className="btn btn-primary">
                {t('btn.select', language) || 'Select Voice Mode'}
              </button>
            </div>
            
            <div className="mode-card" onClick={() => setAssessmentMode('manual')}>
              <div className="mode-icon">📝</div>
              <h2>{t('assessment.manual_mode', language) || 'Manual Mode'}</h2>
              <p>{t('assessment.manual_desc', language) || 'Fill out a detailed form with step-by-step guidance'}</p>
              <div className="mode-features">
                <span className="feature-badge">✓ Detailed</span>
                <span className="feature-badge">✓ Comprehensive</span>
                <span className="feature-badge">✓ Precise</span>
              </div>
              <button className="btn btn-secondary">
                {t('btn.select', language) || 'Select Manual Mode'}
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Voice mode
  if (assessmentMode === 'voice') {
    return (
      <div className="assessment-container">
        <button 
          className="btn btn-secondary mb-3"
          onClick={() => setAssessmentMode(null)}
        >
          ← {t('btn.back', language)}
        </button>
        
        <VoiceAssessment 
          language={language} 
          onComplete={handleVoiceComplete}
        />
      </div>
    )
  }

  // Manual mode - existing form
  // Loading state
  if (loading) {
    return (
      <div className="assessment-container">
        <div className="loading">
          <div className="ai-processing">
            <div className="ai-brain">🤖</div>
            <h2>{t('loading.analyzing', language) || 'AI Analysis in Progress'}</h2>
          </div>
          <div className="spinner"></div>
          <div className="loading-text">
            <strong>{t('loading.processing', language) || 'Our AI is analyzing your health data...'}</strong>
          </div>
        </div>
      </div>
    )
  }

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return renderBasicInfo()
      case 2:
        return renderSymptoms()
      case 3:
        return renderPulse()
      case 4:
        return renderTongue()
      case 5:
        return renderVoice()
      default:
        return null
    }
  }

  const renderBasicInfo = () => (
    <div className="card fade-in">
      <div className="card-header">
        <h2>👤 {t('step.basic', language)}</h2>
      </div>
      <div className="card-body">
        <div className="form-group">
          <label>{t('form.name', language)} *</label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleChange}
            placeholder={t('form.name', language)}
            required
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>{t('form.age', language)} *</label>
            <input
              type="number"
              name="age"
              value={formData.age}
              onChange={handleChange}
              placeholder={t('form.age', language)}
              min="1"
              max="120"
              required
            />
          </div>

          <div className="form-group">
            <label>{t('form.gender', language)} *</label>
            <select name="gender" value={formData.gender} onChange={handleChange}>
              <option value="female">{t('form.female', language)}</option>
              <option value="male">{t('form.male', language)}</option>
              <option value="other">{t('form.other', language)}</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  )

  const renderSymptoms = () => (
    <div className="card fade-in">
      <div className="card-header">
        <h2>📝 {t('step.symptoms', language)}</h2>
      </div>
      <div className="card-body">
        {formData.voiceTranscript && (
          <div className="alert alert-info mb-3">
            <strong>🎤 Voice Input:</strong> "{formData.voiceTranscript}"
            <br />
            <small>Symptoms extracted from your voice recording</small>
          </div>
        )}
        
        <h3 className="mb-2">Common Symptoms</h3>
        <div className="symptom-chips">
          {commonSymptoms.map(symptom => (
            <button
              key={symptom}
              className="chip"
              onClick={() => addSymptom(symptom)}
              disabled={formData.symptoms.find(s => s.name === symptom)}
            >
              + {symptom}
            </button>
          ))}
        </div>

        {formData.symptoms.length > 0 && (
          <div className="symptom-list">
            <h3 className="mb-2">Your Symptoms ({formData.symptoms.length})</h3>
            {formData.symptoms.map((symptom, index) => (
              <div key={index} className="symptom-item">
                <div className="symptom-info">
                  <div className="symptom-name">{symptom.name}</div>
                  <div className="symptom-severity">
                    <label>Severity:</label>
                    <select
                      value={symptom.severity}
                      onChange={(e) => updateSymptomSeverity(index, e.target.value)}
                    >
                      <option value="mild">Mild</option>
                      <option value="moderate">Moderate</option>
                      <option value="severe">Severe</option>
                    </select>
                  </div>
                </div>
                <button
                  className="remove-symptom"
                  onClick={() => removeSymptom(index)}
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )

  const renderPulse = () => (
    <div className="card fade-in">
      <div className="card-header">
        <h2>💓 {t('step.pulse', language)}</h2>
      </div>
      <div className="card-body">
        <div className="pulse-visualizer">
          <div className={`heart-icon ${formData.heartRate > 0 ? 'beating' : ''}`}>
            ❤️
          </div>
          <div className="bpm-display">{formData.heartRate}</div>
          <div className="bpm-label">Beats Per Minute</div>
        </div>

        <div className="slider-container">
          <label>Adjust Heart Rate</label>
          <input
            type="range"
            className="slider"
            min="40"
            max="120"
            value={formData.heartRate}
            onChange={handleHeartRateChange}
          />
          <div className="slider-labels">
            <span>40 BPM</span>
            <span>120 BPM</span>
          </div>
        </div>
      </div>
    </div>
  )

  const renderTongue = () => (
    <div className="card fade-in">
      <div className="card-header">
        <h2>👅 {t('step.tongue', language)}</h2>
      </div>
      <div className="card-body">
        {!formData.tonguePreview ? (
          <div
            className="file-upload"
            onClick={() => fileInputRef.current?.click()}
          >
            <div className="file-upload-icon">📸</div>
            <p><strong>Click to upload</strong></p>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleTongueImageChange}
              style={{ display: 'none' }}
            />
          </div>
        ) : (
          <div className="file-upload has-file">
            <div className="file-preview">
              <img src={formData.tonguePreview} alt="Tongue preview" />
            </div>
            <div className="flex-center gap-2 mt-3">
              <button className="btn btn-secondary" onClick={() => fileInputRef.current?.click()}>
                Change Image
              </button>
              <button className="btn btn-accent" onClick={removeTongueImage}>
                Remove
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )

  const renderVoice = () => (
    <div className="card fade-in">
      <div className="card-header">
        <h2>🎤 {t('step.voice', language)}</h2>
      </div>
      <div className="card-body">
        <p>Voice recording is optional. You can skip this step.</p>
      </div>
    </div>
  )

  return (
    <div className="assessment-container">
      <button 
        className="btn btn-secondary mb-3"
        onClick={() => setAssessmentMode(null)}
      >
        ← Change Mode
      </button>
      
      <div className="progress-container">
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{ width: `${(currentStep / totalSteps) * 100}%` }}
          />
        </div>
        <div className="progress-steps">
          {[
            { num: 1, label: t('step.basic', language) },
            { num: 2, label: t('step.symptoms', language) },
            { num: 3, label: t('step.pulse', language) },
            { num: 4, label: t('step.tongue', language) },
            { num: 5, label: t('step.voice', language) }
          ].map(step => (
            <div key={step.num} className="progress-step">
              <div className={`step-circle ${currentStep === step.num ? 'active' : ''} ${currentStep > step.num ? 'completed' : ''}`}>
                {currentStep > step.num ? '✓' : step.num}
              </div>
              <div className={`step-label ${currentStep === step.num ? 'active' : ''}`}>
                {step.label}
              </div>
            </div>
          ))}
        </div>
      </div>

      {error && (
        <div className="alert alert-error">
          <span>⚠️</span>
          <span>{error}</span>
        </div>
      )}

      {renderStep()}

      <div className="step-actions">
        <button
          className="btn btn-secondary"
          onClick={handleBack}
          disabled={currentStep === 1}
        >
          ← {t('btn.back', language)}
        </button>
        <button
          className="btn btn-primary"
          onClick={handleNext}
        >
          {currentStep === totalSteps ? t('btn.submit', language) : t('btn.next', language)} →
        </button>
      </div>
    </div>
  )
}

export default AssessmentEnhanced
