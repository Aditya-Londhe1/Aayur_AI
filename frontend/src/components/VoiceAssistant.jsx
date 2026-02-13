import { useState, useEffect, useRef } from 'react';
import voiceAssistantService from '../services/voiceAssistantService';
import VoiceFileUpload from './VoiceFileUpload';

const VoiceAssistant = () => {
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [language, setLanguage] = useState('en');
  const [extractedInfo, setExtractedInfo] = useState(null);
  const [error, setError] = useState(null);

  const recognitionRef = useRef(null);
  const synthRef = useRef(window.speechSynthesis);
  const messagesEndRef = useRef(null);
  const handleUserMessageRef = useRef(null);

  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize Speech Recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      
      // Auto-detect language or use selected
      if (language !== 'en') {
        const langMap = {
          'hi': 'hi-IN',
          'ta': 'ta-IN',
          'te': 'te-IN',
          'bn': 'bn-IN',
          'mr': 'mr-IN',
          'gu': 'gu-IN',
          'kn': 'kn-IN',
          'ml': 'ml-IN',
          'pa': 'pa-IN',
          'or': 'or-IN',
        };
        recognitionRef.current.lang = langMap[language] || 'en-US';
      } else {
        recognitionRef.current.lang = 'en-US';
      }

      recognitionRef.current.onresult = (event) => {
        console.log('Speech recognition result:', event.results);
        const transcript = event.results[0][0].transcript;
        console.log('Transcript:', transcript);
        console.log('Confidence:', event.results[0][0].confidence);
        console.log('Calling handleUserMessage with:', transcript);
        
        // Use ref to get latest handleUserMessage
        if (handleUserMessageRef.current && transcript && transcript.trim()) {
          handleUserMessageRef.current(transcript);
        } else {
          console.error('handleUserMessage not available or empty transcript');
        }
      };

      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        console.error('Error details:', event);
        setIsListening(false);
        setError(`Could not understand: ${event.error}. Please try again.`);
      };

      recognitionRef.current.onstart = () => {
        console.log('Speech recognition started');
      };

      recognitionRef.current.onend = () => {
        console.log('Speech recognition ended');
        setIsListening(false);
      };

      recognitionRef.current.onnomatch = () => {
        console.log('Speech recognition: no match');
        setError('No speech detected. Please try again.');
        setIsListening(false);
      };

      recognitionRef.current.onaudiostart = () => {
        console.log('Audio capturing started');
      };

      recognitionRef.current.onaudioend = () => {
        console.log('Audio capturing ended');
      };

      recognitionRef.current.onspeechstart = () => {
        console.log('Speech detected');
      };

      recognitionRef.current.onspeechend = () => {
        console.log('Speech ended');
      };
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      synthRef.current.cancel();
    };
  }, [language]);

  // Start new session
  const startSession = async () => {
    try {
      setError(null);
      setIsProcessing(true);
      
      console.log('Starting session with language:', language);
      const response = await voiceAssistantService.startSession(language);
      console.log('Session response:', response);
      
      if (response.success) {
        setSessionId(response.conversation_id || response.session_id);  // Support both
        const aiMessage = {
          role: 'assistant',
          content: response.message,
          timestamp: new Date().toISOString(),
        };
        setMessages([aiMessage]);
        
        console.log('AI greeting:', response.message);
        
        // Speak the greeting
        speak(response.message);
      } else {
        console.error('Session start failed:', response);
        setError('Failed to start session');
      }
    } catch (err) {
      console.error('Error starting session:', err);
      setError('Failed to start session. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  // Handle user message
  const handleUserMessage = async (text) => {
    if (!sessionId || !text.trim()) {
      console.log('Cannot send message:', { sessionId, text });
      return;
    }

    try {
      setError(null);
      setIsProcessing(true);

      console.log('Sending message:', text, 'Language:', language);

      // Add user message to chat
      const userMessage = {
        role: 'user',
        content: text,
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, userMessage]);

      // Send to backend
      const response = await voiceAssistantService.chat(sessionId, text, language);
      console.log('Chat response:', response);

      if (response.success) {
        // Add AI response to chat
        const aiMessage = {
          role: 'assistant',
          content: response.message,
          timestamp: new Date().toISOString(),
        };
        setMessages(prev => [...prev, aiMessage]);

        console.log('AI response:', response.message);

        // Update extracted info
        if (response.extracted_info) {
          setExtractedInfo(response.extracted_info);
          console.log('Extracted info:', response.extracted_info);
        }

        // Speak the response
        speak(response.message);
      } else {
        console.error('Chat failed:', response);
        setError('Failed to get response');
      }
    } catch (err) {
      console.error('Error in chat:', err);
      setError('Failed to process message. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  // Update ref whenever handleUserMessage changes
  useEffect(() => {
    handleUserMessageRef.current = handleUserMessage;
  }, [sessionId, language, messages]);

  // Start listening
  const startListening = () => {
    if (!sessionId) {
      setError('Please start a session first');
      return;
    }

    if (recognitionRef.current && !isListening) {
      console.log('Starting speech recognition...');
      console.log('Recognition object:', recognitionRef.current);
      console.log('Language:', recognitionRef.current.lang);
      
      setError(null);
      setIsListening(true);
      
      try {
        recognitionRef.current.start();
        console.log('Recognition.start() called successfully');
      } catch (error) {
        console.error('Error starting recognition:', error);
        setError(`Failed to start microphone: ${error.message}`);
        setIsListening(false);
      }
    } else {
      console.log('Cannot start listening:', {
        hasRecognition: !!recognitionRef.current,
        isListening,
        sessionId
      });
    }
  };

  // Stop listening
  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    }
  };

  // Text-to-Speech
  const speak = (text) => {
    if (!text) {
      console.log('No text to speak');
      return;
    }

    console.log('Speaking:', text, 'Language:', language);

    // Cancel any ongoing speech
    synthRef.current.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    
    // Set language
    const langMap = {
      'hi': 'hi-IN',
      'ta': 'ta-IN',
      'te': 'te-IN',
      'bn': 'bn-IN',
      'en': 'en-US',
    };
    utterance.lang = langMap[language] || 'en-US';
    utterance.rate = 0.9;
    utterance.pitch = 1;

    console.log('TTS language:', utterance.lang);

    utterance.onstart = () => {
      console.log('TTS started');
      setIsSpeaking(true);
    };
    utterance.onend = () => {
      console.log('TTS ended');
      setIsSpeaking(false);
    };
    utterance.onerror = (e) => {
      console.error('TTS error:', e);
      setIsSpeaking(false);
    };

    synthRef.current.speak(utterance);
  };

  // Stop speaking
  const stopSpeaking = () => {
    synthRef.current.cancel();
    setIsSpeaking(false);
  };

  // End session
  const endSession = async () => {
    if (sessionId) {
      try {
        await voiceAssistantService.endSession(sessionId);
      } catch (err) {
        console.error('Error ending session:', err);
      }
    }
    setSessionId(null);
    setMessages([]);
    setExtractedInfo(null);
    setError(null);
    stopSpeaking();
  };

  return (
    <div className="voice-assistant-container">
      <div className="voice-assistant-header">
        <h2>🎤 AI Voice Assistant</h2>
        <p>Speak naturally about your health concerns in any language</p>
      </div>

      {/* Language Selector */}
      <div className="language-selector">
        <label>Language:</label>
        <select 
          value={language} 
          onChange={(e) => setLanguage(e.target.value)}
          disabled={sessionId !== null}
        >
          <option value="en">English</option>
          <option value="hi">हिंदी (Hindi)</option>
          <option value="ta">தமிழ் (Tamil)</option>
          <option value="te">తెలుగు (Telugu)</option>
          <option value="bn">বাংলা (Bengali)</option>
          <option value="mr">मराठी (Marathi)</option>
          <option value="gu">ગુજરાતી (Gujarati)</option>
          <option value="kn">ಕನ್ನಡ (Kannada)</option>
          <option value="ml">മലയാളം (Malayalam)</option>
          <option value="pa">ਪੰਜਾਬੀ (Punjabi)</option>
        </select>
      </div>

      {/* Error Message */}
      {error && (
        <div className="error-message">
          ⚠️ {error}
        </div>
      )}

      {/* Session Controls */}
      <div className="session-controls">
        {!sessionId ? (
          <button 
            className="btn-primary btn-large"
            onClick={startSession}
            disabled={isProcessing}
          >
            {isProcessing ? '⏳ Starting...' : '🚀 Start Conversation'}
          </button>
        ) : (
          <button 
            className="btn-secondary"
            onClick={endSession}
          >
            ❌ End Session
          </button>
        )}
      </div>

      {/* Chat Messages */}
      {sessionId && (
        <div className="chat-container">
          <div className="messages-list">
            {messages.map((msg, index) => (
              <div 
                key={index} 
                className={`message ${msg.role === 'user' ? 'user-message' : 'ai-message'}`}
              >
                <div className="message-icon">
                  {msg.role === 'user' ? '👤' : '🤖'}
                </div>
                <div className="message-content">
                  <p>{msg.content}</p>
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          {/* Voice Controls */}
          <div className="voice-controls">
            {!isListening ? (
              <button 
                className="btn-voice btn-listen"
                onClick={startListening}
                disabled={isProcessing || isSpeaking}
              >
                {isProcessing ? '⏳ Processing...' : '🎤 Speak'}
              </button>
            ) : (
              <button 
                className="btn-voice btn-listening"
                onClick={stopListening}
              >
                🔴 Listening...
              </button>
            )}

            {isSpeaking && (
              <button 
                className="btn-voice btn-stop-speaking"
                onClick={stopSpeaking}
              >
                🔇 Stop Speaking
              </button>
            )}
          </div>

          {/* Voice File Upload */}
          <VoiceFileUpload
            conversationId={sessionId}
            language={language}
            onUploadComplete={(result) => {
              console.log('Voice file uploaded:', result);
              
              // Add transcribed text as user message
              if (result.transcribed_text) {
                const userMessage = {
                  role: 'user',
                  content: result.transcribed_text,
                  timestamp: new Date().toISOString(),
                };
                setMessages(prev => [...prev, userMessage]);
              }
              
              // Add AI response
              if (result.message) {
                const aiMessage = {
                  role: 'assistant',
                  content: result.message,
                  timestamp: new Date().toISOString(),
                };
                setMessages(prev => [...prev, aiMessage]);
                
                // Speak the response
                speak(result.message);
              }
              
              // Update extracted info
              if (result.extracted_info) {
                setExtractedInfo(result.extracted_info);
              }
            }}
            onError={(error) => {
              setError(error);
            }}
          />

          {/* Extracted Information */}
          {extractedInfo && extractedInfo.symptoms && extractedInfo.symptoms.length > 0 && (
            <div className="extracted-info">
              <h3>📋 Information Collected</h3>
              <div className="info-section">
                <h4>Symptoms:</h4>
                <ul>
                  {extractedInfo.symptoms.map((symptom, idx) => (
                    <li key={idx}>
                      {symptom.name}
                      {symptom.severity && ` (${symptom.severity})`}
                      {symptom.duration && ` - ${symptom.duration}`}
                    </li>
                  ))}
                </ul>
              </div>
              {extractedInfo.patient_info && Object.keys(extractedInfo.patient_info).length > 0 && (
                <div className="info-section">
                  <h4>Patient Info:</h4>
                  <ul>
                    {extractedInfo.patient_info.age && <li>Age: {extractedInfo.patient_info.age}</li>}
                    {extractedInfo.patient_info.gender && <li>Gender: {extractedInfo.patient_info.gender}</li>}
                  </ul>
                </div>
              )}
              {extractedInfo.ready_for_assessment && (
                <div className="assessment-ready">
                  ✅ Ready for assessment! You can proceed to diagnosis.
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Browser Support Warning */}
      {!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) && (
        <div className="warning-message">
          ⚠️ Voice recognition is not supported in your browser. Please use Chrome, Edge, or Safari.
        </div>
      )}
    </div>
  );
};

export default VoiceAssistant;
