import React, { useState, useRef, useEffect } from 'react'
import { t } from '../i18n/translations'

const API_URL = 'http://localhost:8000/api/v1'

function VoiceAssessment({ language, onComplete }) {
  const [isListening, setIsListening] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [extractedSymptoms, setExtractedSymptoms] = useState([])
  const [error, setError] = useState(null)
  const [audioBlob, setAudioBlob] = useState(null)
  const [useWebSpeech, setUseWebSpeech] = useState(true)
  
  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])
  const recognitionRef = useRef(null)

  // Check if Web Speech API is available
  useEffect(() => {
    const hasWebSpeech = 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window
    setUseWebSpeech(hasWebSpeech)
    
    if (!hasWebSpeech) {
      console.warn('Web Speech API not available, will use backend processing only')
    }
  }, [])

  // Initialize Web Speech API if available
  useEffect(() => {
    if (!useWebSpeech) return
    
    try {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
      recognitionRef.current = new SpeechRecognition()
      recognitionRef.current.continuous = false  // Changed to false for better accuracy
      recognitionRef.current.interimResults = false  // Changed to false to avoid duplicates
      recognitionRef.current.maxAlternatives = 1
      
      // Map language codes to speech recognition
      const langMap = {
        'en': 'en-US',
        'hi': 'hi-IN',
        'ta': 'ta-IN',
        'te': 'te-IN',
        'bn': 'bn-IN',
        'gu': 'gu-IN',
        'kn': 'kn-IN',
        'ml': 'ml-IN',
        'mr': 'mr-IN',
        'pa': 'pa-IN',
        'or': 'or-IN'
      }
      recognitionRef.current.lang = langMap[language] || 'en-US'
      
      recognitionRef.current.onresult = (event) => {
        const result = event.results[event.results.length - 1]
        if (result.isFinal) {
          const transcriptText = result[0].transcript
          setTranscript(prev => {
            // Avoid duplicates by checking if text already exists
            if (prev.includes(transcriptText)) {
              return prev
            }
            return prev ? prev + ' ' + transcriptText : transcriptText
          })
          
          // Restart recognition if still listening
          if (isListening) {
            try {
              recognitionRef.current.start()
            } catch (err) {
              // Already started, ignore
            }
          }
        }
      }
      
      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error)
        if (event.error === 'no-speech') {
          // Restart if no speech detected
          if (isListening) {
            try {
              recognitionRef.current.start()
            } catch (err) {
              // Already started, ignore
            }
          }
        } else if (event.error !== 'aborted') {
          setError(`Voice recognition error: ${event.error}. Will use audio recording instead.`)
        }
      }
      
      recognitionRef.current.onend = () => {
        // Restart if still listening
        if (isListening) {
          try {
            recognitionRef.current.start()
          } catch (err) {
            // Already started or stopped, ignore
          }
        }
      }
    } catch (err) {
      console.error('Failed to initialize speech recognition:', err)
      setUseWebSpeech(false)
    }
  }, [language, useWebSpeech, isListening])

  const startVoiceRecording = async () => {
    try {
      setError(null)
      setTranscript('')
      audioChunksRef.current = []
      
      // Start audio recording for backend processing
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      mediaRecorderRef.current = new MediaRecorder(stream)
      
      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }
      
      mediaRecorderRef.current.onstop = () => {
        const blob = new Blob(audioChunksRef.current, { type: 'audio/wav' })
        setAudioBlob(blob)
        stream.getTracks().forEach(track => track.stop())
      }
      
      mediaRecorderRef.current.start()
      
      // Start speech recognition for real-time feedback (if available)
      if (useWebSpeech && recognitionRef.current) {
        try {
          recognitionRef.current.start()
        } catch (err) {
          console.warn('Could not start speech recognition:', err)
        }
      }
      
      setIsListening(true)
    } catch (err) {
      setError('Could not access microphone. Please check permissions and try again.')
      console.error('Microphone error:', err)
    }
  }

  const stopVoiceRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop()
    }
    
    if (useWebSpeech && recognitionRef.current) {
      try {
        recognitionRef.current.stop()
      } catch (err) {
        console.warn('Could not stop speech recognition:', err)
      }
    }
    
    setIsListening(false)
  }

  const processVoiceInput = async () => {
    if (!transcript) {
      setError('No voice input recorded. Please try again.')
      return
    }
    
    setIsProcessing(true)
    setError(null)
    
    try {
      // Send transcript to backend for processing
      console.log('Sending transcript to backend:', transcript)
      
      const formData = new FormData()
      formData.append('text', transcript)
      formData.append('language', language || 'en')
      
      const response = await fetch(`${API_URL}/voice/extract-symptoms-from-text`, {
        method: 'POST',
        body: formData
      })
      
      if (!response.ok) {
        throw new Error('Backend processing failed')
      }
      
      const result = await response.json()
      console.log('Backend response:', result)
      
      if (result.success && result.extracted_symptoms) {
        setExtractedSymptoms(result.extracted_symptoms)
        
        // Pass results to parent
        if (onComplete) {
          onComplete({
            symptoms: result.extracted_symptoms,
            transcript: transcript,
            confidence: result.confidence || 0.75
          })
        }
      } else {
        setError(result.error || 'No symptoms could be extracted. Please try manual mode.')
      }
      
    } catch (err) {
      setError(err.message || 'Failed to process voice input. Please try manual mode.')
      console.error('Voice processing error:', err)
    } finally {
      setIsProcessing(false)
    }
  }

  return (
    <div className="voice-assessment">
      <div className="voice-header">
        <h2>🎤 {t('voice.speak', language)}</h2>
        <p className="voice-subtitle">{t('voice.instructions', language)}</p>
        {!useWebSpeech && (
          <div className="alert alert-info">
            <small>Real-time transcription not available in this browser. Your audio will be processed by our server.</small>
          </div>
        )}
      </div>

      <div className="voice-interface">
        {!isListening && !transcript ? (
          <button
            className="voice-button voice-button-start"
            onClick={startVoiceRecording}
            disabled={isProcessing}
          >
            <span className="voice-icon">🎤</span>
            <span>{t('btn.record', language)}</span>
          </button>
        ) : isListening ? (
          <div className="voice-listening">
            <button
              className="voice-button voice-button-stop"
              onClick={stopVoiceRecording}
            >
              <span className="voice-icon pulse-animation">🔴</span>
              <span>{t('btn.stop', language)}</span>
            </button>
            <p className="listening-text">{t('voice.listening', language)}</p>
            {transcript && (
              <div className="live-transcript">
                <p>{transcript}</p>
              </div>
            )}
          </div>
        ) : (
          <div className="voice-complete">
            <div className="transcript-box">
              <div className="transcript-header">
                <h3>Transcript:</h3>
                <button 
                  className="btn-link"
                  onClick={() => {
                    setTranscript('')
                    setExtractedSymptoms([])
                  }}
                  style={{ fontSize: '0.875rem', color: 'var(--primary)' }}
                >
                  Clear
                </button>
              </div>
              <p>{transcript || 'Recording complete. Click Continue to process.'}</p>
              <small className="text-secondary">
                {transcript ? `${transcript.split(' ').length} words recorded` : ''}
              </small>
            </div>
            
            {extractedSymptoms.length > 0 && (
              <div className="extracted-symptoms">
                <h3>✅ Extracted Symptoms:</h3>
                <ul>
                  {extractedSymptoms.map((symptom, idx) => (
                    <li key={idx}>
                      <strong>{symptom.name || symptom}</strong>
                      {symptom.severity && ` (${symptom.severity})`}
                    </li>
                  ))}
                </ul>
                <small className="text-secondary">
                  {extractedSymptoms.length} symptom{extractedSymptoms.length !== 1 ? 's' : ''} found
                </small>
              </div>
            )}
            
            <div className="voice-actions">
              <button
                className="btn btn-secondary"
                onClick={() => {
                  setTranscript('')
                  setExtractedSymptoms([])
                  setAudioBlob(null)
                }}
              >
                Record Again
              </button>
              <button
                className="btn btn-primary"
                onClick={processVoiceInput}
                disabled={isProcessing || !transcript}
              >
                {isProcessing ? t('voice.processing', language) : 
                 extractedSymptoms.length > 0 ? 'Add Symptoms & Continue' : 'Extract Symptoms'}
              </button>
            </div>
          </div>
        )}
      </div>

      {error && (
        <div className="alert alert-error">
          <span>⚠️</span>
          <span>{error}</span>
        </div>
      )}

      <div className="voice-tips">
        <h4>💡 Tips for Best Results:</h4>
        <ul>
          <li>Speak clearly in a quiet environment</li>
          <li>Describe your symptoms in detail</li>
          <li>Mention duration and severity if possible</li>
          <li>Use your native language for comfort</li>
          <li>If voice doesn't work, you can switch to manual mode</li>
        </ul>
      </div>
    </div>
  )
}

export default VoiceAssessment
