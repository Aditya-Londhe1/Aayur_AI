import React, { useState, useRef, useEffect } from 'react'
import useSpeechRecognition from '../hooks/useSpeechRecognition'
import { useNavigate } from 'react-router-dom'

const API_URL = 'http://localhost:8000/api/v1'

function Assessment({ language }) {
  const navigate = useNavigate()
  const [currentStep, setCurrentStep] = useState(1)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // Form data state
  const [formData, setFormData] = useState({
    // Step 1: Basic Info
    name: '',
    age: '',
    gender: 'female',
    weight: '',
    height: '',

    // Step 2: Symptoms
    symptoms: [],
    customSymptom: '',

    // Step 3: Pulse Data
    heartRate: 72,
    pulseData: null,

    // Step 4: Tongue Image
    tongueImage: null,
    tonguePreview: null,

    // Step 5: Voice Recording
    voiceAudio: null,
    voicePreview: null
  })

  // Voice Hook
  const { isListening, transcript, startListening, stopListening } = useSpeechRecognition()

  // Update custom symptom with voice
  useEffect(() => {
    if (transcript) {
      setFormData(prev => ({
        ...prev,
        customSymptom: prev.customSymptom ? `${prev.customSymptom} ${transcript}` : transcript
      }))
    }
  }, [transcript])

  // TTS Instructions
  useEffect(() => {
    const instructions = {
      1: "Welcome. Please enter your basic details.",
      2: "Select symptoms or speak them using the microphone.",
      3: "Adjust the slider to match your heart rate.",
      4: "Upload a photo of your tongue.",
      5: "Record a voice sample."
    }
    const msg = instructions[currentStep]
    if (msg) {
      const utterance = new SpeechSynthesisUtterance(msg)
      window.speechSynthesis.cancel()
      window.speechSynthesis.speak(utterance)
    }
  }, [currentStep])

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
    'Cough', 'Cold', 'Fever', 'Sore Throat',
    'Weight Gain', 'Weight Loss', 'Poor Appetite', 'Excessive Hunger',
    'Irritability', 'Depression', 'Stress', 'Mood Swings',
    'Excessive Sweating', 'Cold Hands/Feet', 'Hot Flashes', 'Night Sweats',
    'Bloating', 'Gas', 'Indigestion', 'Heartburn',
    'Irregular Periods', 'Heavy Periods', 'PMS', 'Menopause Symptoms'
  ]

  // Handle form field changes
  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  // Step 1: Basic Info validation
  const validateStep1 = () => {
    if (!formData.name.trim()) {
      setError('Please enter your name')
      return false
    }
    if (!formData.age || formData.age < 1 || formData.age > 120) {
      setError('Please enter a valid age (1-120)')
      return false
    }
    return true
  }

  // Step 2: Add symptom
  const addSymptom = (symptomName) => {
    if (formData.symptoms.find(s => s.name.toLowerCase() === symptomName.toLowerCase())) {
      return // Already added
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

  // Step 3: Generate pulse data from heart rate
  const generatePulseData = (bpm) => {
    const duration = 60 // seconds
    const samplingRate = 50 // Hz
    const totalPoints = duration * samplingRate
    const frequency = bpm / 60

    const wave = []
    for (let i = 0; i < totalPoints; i++) {
      const t = i / samplingRate
      // Simulate cardiac cycle
      const signal = Math.sin(2 * Math.PI * frequency * t) +
        0.5 * Math.sin(4 * Math.PI * frequency * t) +
        (Math.random() - 0.5) * 0.1 // Add noise
      wave.push(signal)
    }
    return wave
  }

  const handleHeartRateChange = (e) => {
    const hr = parseInt(e.target.value)
    setFormData(prev => ({
      ...prev,
      heartRate: hr,
      pulseData: generatePulseData(hr)
    }))
  }

  // Step 4: Handle tongue image upload
  const handleTongueImageChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      if (!file.type.startsWith('image/')) {
        setError('Please upload an image file')
        return
      }
      if (file.size > 5 * 1024 * 1024) { // 5MB limit
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

  // Step 5: Handle voice recording
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      mediaRecorderRef.current = new MediaRecorder(stream)
      audioChunksRef.current = []

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }

      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' })
        setFormData(prev => ({
          ...prev,
          voiceAudio: audioBlob,
          voicePreview: URL.createObjectURL(audioBlob)
        }))
        stream.getTracks().forEach(track => track.stop())
      }

      mediaRecorderRef.current.start()
      setError(null)
    } catch (err) {
      setError('Could not access microphone. Please check permissions.')
      console.error('Microphone error:', err)
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop()
    }
  }

  const removeVoiceRecording = () => {
    setFormData(prev => ({
      ...prev,
      voiceAudio: null,
      voicePreview: null
    }))
  }

  const isRecording = mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording'

  // Navigation
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

  // Submit assessment
  const handleSubmit = async () => {
    setLoading(true)
    setError(null)

    try {
      // Prepare form data for API
      const apiFormData = new FormData()
      apiFormData.append('patient_name', formData.name)
      apiFormData.append('patient_age', formData.age)
      apiFormData.append('patient_gender', formData.gender)

      // Add symptoms if any
      if (formData.symptoms.length > 0) {
        apiFormData.append('symptoms', JSON.stringify(formData.symptoms))
      }

      // Add pulse data if available
      if (formData.pulseData) {
        apiFormData.append('pulse_data', JSON.stringify(formData.pulseData))
      }

      // Add tongue image if available
      if (formData.tongueImage) {
        apiFormData.append('tongue_image', formData.tongueImage)
      }

      apiFormData.append('locale', language || 'en')

      // Call complete consultation API
      const response = await fetch(`${API_URL}/consultations/complete`, {
        method: 'POST',
        body: apiFormData
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Analysis failed')
      }

      const result = await response.json()

      // Navigate to results page with data
      navigate('/results', { state: { result: result.analysis, patientInfo: formData } })

    } catch (err) {
      setError(err.message || 'Failed to complete assessment. Please try again.')
      console.error('Assessment error:', err)
    } finally {
      setLoading(false)
    }
  }

  // Render current step
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

  // Step 1: Basic Information
  const renderBasicInfo = () => (
    <div className="card fade-in">
      <div className="card-header">
        <h2>👤 Basic Information</h2>
        <div className="ai-indicator-small">🤖 AI will personalize based on your profile</div>
      </div>
      <div className="card-body">
        <div className="form-group">
          <label>Full Name *</label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleChange}
            placeholder="Enter your full name"
            required
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Age *</label>
            <input
              type="number"
              name="age"
              value={formData.age}
              onChange={handleChange}
              placeholder="Age"
              min="1"
              max="120"
              required
            />
          </div>

          <div className="form-group">
            <label>Gender *</label>
            <select name="gender" value={formData.gender} onChange={handleChange}>
              <option value="female">Female</option>
              <option value="male">Male</option>
              <option value="other">Other</option>
            </select>
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Weight (kg)</label>
            <input
              type="number"
              name="weight"
              value={formData.weight}
              onChange={handleChange}
              placeholder="Weight in kg"
              min="1"
            />
            <div className="form-help">Optional: Helps with personalized recommendations</div>
          </div>

          <div className="form-group">
            <label>Height (cm)</label>
            <input
              type="number"
              name="height"
              value={formData.height}
              onChange={handleChange}
              placeholder="Height in cm"
              min="1"
            />
            <div className="form-help">Optional: Helps with personalized recommendations</div>
          </div>
        </div>
      </div>
    </div>
  )

  // Step 2: Symptoms
  const renderSymptoms = () => (
    <div className="card fade-in">
      <div className="card-header">
        <h2>📝 Symptoms & Health Concerns</h2>
        <div className="ai-indicator-small">🤖 AI NLP will analyze symptom patterns</div>
      </div>
      <div className="card-body">
        <p className="text-secondary mb-3">
          Select common symptoms or add your own. You can skip this step if you have no specific concerns.
        </p>

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

        <div className="form-group mt-4">
          <label>Add Custom Symptom</label>
          <div className="flex gap-2">
            <button
              className={`mic-button ${isListening ? 'listening' : ''}`}
              onClick={isListening ? stopListening : startListening}
              title="Speak symptom"
            >
              {isListening ? '⏹️' : '🎤'}
            </button>
            <input
              type="text"
              name="customSymptom"
              value={formData.customSymptom}
              onChange={handleChange}
              placeholder="Type your symptom..."
              onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addCustomSymptom())}
            />
            <button className="btn btn-primary" onClick={addCustomSymptom}>
              Add
            </button>
          </div>
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
                  title="Remove symptom"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        )}

        {formData.symptoms.length === 0 && (
          <div className="alert alert-info mt-3">
            No symptoms added yet. You can skip this step if you're feeling well.
          </div>
        )}
      </div>
    </div>
  )

  // Step 3: Pulse Data
  const renderPulse = () => (
    <div className="card fade-in">
      <div className="card-header">
        <h2>💓 Pulse Analysis</h2>
        <div className="ai-indicator-small">🤖 AI signal processing for Nadi Pariksha</div>
      </div>
      <div className="card-body">
        <p className="text-secondary mb-3">
          Adjust the slider to match your current heart rate. This will be used for Nadi Pariksha (pulse diagnosis).
        </p>

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

        <div className="alert alert-info mt-3">
          <strong>Tip:</strong> Measure your pulse by placing two fingers on your wrist or neck and counting beats for 15 seconds, then multiply by 4.
        </div>

        <div className="alert alert-warning mt-2">
          <strong>Note:</strong> For best results, measure your pulse while sitting calmly. Normal resting heart rate is 60-100 BPM.
        </div>
      </div>
    </div>
  )

  // Step 4: Tongue Analysis
  const renderTongue = () => (
    <div className="card fade-in">
      <div className="card-header">
        <h2>👅 Tongue Analysis</h2>
        <div className="ai-indicator-small">🤖 AI Computer Vision will analyze your tongue</div>
      </div>
      <div className="card-body">
        <p className="text-secondary mb-3">
          Upload a clear photo of your tongue in natural light. This is optional but provides valuable diagnostic information.
        </p>

        <div className="alert alert-info mb-3">
          <strong>Tips for best results:</strong>
          <ul style={{ marginTop: '0.5rem', paddingLeft: '1.5rem' }}>
            <li>Take photo in natural daylight</li>
            <li>Stick tongue out fully</li>
            <li>Keep tongue relaxed</li>
            <li>Avoid colored foods/drinks before photo</li>
            <li>Clean your tongue gently before photo</li>
          </ul>
        </div>

        {!formData.tonguePreview ? (
          <div
            className="file-upload"
            onClick={() => fileInputRef.current?.click()}
          >
            <div className="file-upload-icon">📸</div>
            <p><strong>Click to upload</strong> or drag and drop</p>
            <p className="text-secondary">JPG, PNG up to 5MB</p>
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

        <div className="alert alert-warning mt-3">
          <strong>Privacy:</strong> Your image is processed securely and not stored permanently.
        </div>
      </div>
    </div>
  )

  // Step 5: Voice Recording
  const renderVoice = () => (
    <div className="card fade-in">
      <div className="card-header">
        <h2>🎤 Voice Analysis</h2>
        <div className="ai-indicator-small">🤖 AI will extract acoustic biomarkers</div>
      </div>
      <div className="card-body">
        <p className="text-secondary mb-3">
          Record a short voice sample (10-30 seconds) for acoustic biomarker analysis. This is optional.
        </p>

        <div className="alert alert-info mb-3">
          <strong>What to say:</strong> Read a short passage, describe your symptoms, or simply count from 1 to 20 in a normal speaking voice.
        </div>

        <div className="audio-recorder">
          {!formData.voicePreview ? (
            <>
              <button
                className={`record-button ${isRecording ? 'recording' : ''}`}
                onClick={isRecording ? stopRecording : startRecording}
              >
                {isRecording ? '⏹️' : '🎤'}
              </button>
              <p className="mt-3">
                {isRecording ? 'Recording... Click to stop' : 'Click to start recording'}
              </p>
            </>
          ) : (
            <div className="audio-preview">
              <p className="mb-2"><strong>Recording Complete</strong></p>
              <audio controls src={formData.voicePreview} />
              <div className="flex-center gap-2 mt-3">
                <button className="btn btn-secondary" onClick={startRecording}>
                  Re-record
                </button>
                <button className="btn btn-accent" onClick={removeVoiceRecording}>
                  Remove
                </button>
              </div>
            </div>
          )}
        </div>

        <div className="alert alert-warning mt-3">
          <strong>Privacy:</strong> Your voice recording is processed securely and not stored permanently.
        </div>
      </div>
    </div>
  )

  // Loading state
  if (loading) {
    return (
      <div className="assessment-container">
        <div className="loading">
          <div className="ai-processing">
            <div className="ai-brain">🤖</div>
            <h2>AI Analysis in Progress</h2>
          </div>
          <div className="spinner"></div>
          <div className="loading-text">
            <strong>Our AI is analyzing your health data...</strong>
            <br />
            <small>This may take a few moments</small>
          </div>
          <div className="ai-steps">
            <div className="ai-step">
              <span className="ai-step-icon">🧠</span>
              <span>Processing with Deep Learning Models</span>
            </div>
            <div className="ai-step">
              <span className="ai-step-icon">👁️</span>
              <span>Analyzing Visual Features (if image provided)</span>
            </div>
            <div className="ai-step">
              <span className="ai-step-icon">💬</span>
              <span>Understanding Symptoms with NLP</span>
            </div>
            <div className="ai-step">
              <span className="ai-step-icon">📊</span>
              <span>Processing Pulse Signals</span>
            </div>
            <div className="ai-step">
              <span className="ai-step-icon">🔗</span>
              <span>Fusing Multi-Modal Data</span>
            </div>
            <div className="ai-step">
              <span className="ai-step-icon">✨</span>
              <span>Generating Personalized Recommendations</span>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="assessment-container">
      {/* Progress Bar */}
      <div className="progress-container">
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{ width: `${(currentStep / totalSteps) * 100}%` }}
          />
        </div>
        <div className="progress-steps">
          {[
            { num: 1, label: 'Basic Info' },
            { num: 2, label: 'Symptoms' },
            { num: 3, label: 'Pulse' },
            { num: 4, label: 'Tongue' },
            { num: 5, label: 'Voice' }
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

      {/* Error Alert */}
      {error && (
        <div className="alert alert-error">
          <span>⚠️</span>
          <span>{error}</span>
        </div>
      )}

      {/* Current Step Content */}
      {renderStep()}

      {/* Navigation Buttons */}
      <div className="step-actions">
        <button
          className="btn btn-secondary"
          onClick={handleBack}
          disabled={currentStep === 1}
        >
          ← Back
        </button>
        <button
          className="btn btn-primary"
          onClick={handleNext}
        >
          {currentStep === totalSteps ? 'Complete Assessment →' : 'Next →'}
        </button>
      </div>
    </div>
  )
}

export default Assessment
