import { useState } from 'react';
import voiceAssistantService from '../services/voiceAssistantService';
import '../styles/animations.css';

const VoiceFileUpload = ({ conversationId, language, onUploadComplete, onError }) => {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [fileName, setFileName] = useState('');
  const [uploadProgress, setUploadProgress] = useState(0);
  
  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    
    // Validate file type
    if (!file.type.startsWith('audio/')) {
      const errorMsg = 'Please upload an audio file (MP3, WAV, OGG, M4A)';
      setError(errorMsg);
      if (onError) onError(errorMsg);
      return;
    }
    
    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      const errorMsg = 'File size must be less than 10MB';
      setError(errorMsg);
      if (onError) onError(errorMsg);
      return;
    }
    
    setFileName(file.name);
    setUploading(true);
    setError(null);
    setUploadProgress(0);
    
    try {
      console.log('Uploading voice file:', file.name);
      
      // Simulate progress (since we don't have real progress tracking)
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 10, 90));
      }, 200);
      
      const result = await voiceAssistantService.uploadVoice(
        file,
        conversationId,
        language
      );
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      
      console.log('Upload result:', result);
      
      if (result.success) {
        if (onUploadComplete) {
          onUploadComplete(result);
        }
        // Clear file input after short delay
        setTimeout(() => {
          event.target.value = '';
          setFileName('');
          setUploadProgress(0);
        }, 1500);
      } else {
        const errorMsg = result.error || 'Upload failed';
        setError(errorMsg);
        if (onError) onError(errorMsg);
        setUploadProgress(0);
      }
    } catch (err) {
      console.error('Upload error:', err);
      const errorMsg = 'Failed to upload audio file. Please check your connection and try again.';
      setError(errorMsg);
      if (onError) onError(errorMsg);
      setUploadProgress(0);
    } finally {
      setUploading(false);
    }
  };
  
  return (
    <div className="voice-file-upload fade-in" style={styles.container}>
      <label style={styles.uploadButton} className="button-hover">
        <input
          type="file"
          accept="audio/*"
          onChange={handleFileUpload}
          disabled={uploading}
          style={{ display: 'none' }}
        />
        <span style={styles.buttonContent}>
          {uploading ? (
            <>
              <span className="pulse">{uploadProgress}%</span>
            </>
          ) : (
            <>
              <span style={styles.icon}>📁</span>
              <span>Upload Audio File</span>
            </>
          )}
        </span>
      </label>
      
      {uploading && uploadProgress > 0 && (
        <div style={styles.progressBar} className="fade-in">
          <div 
            style={{...styles.progressFill, width: `${uploadProgress}%`}} 
            className="progress-bar"
          />
        </div>
      )}
      
      {fileName && !uploading && !error && (
        <div style={styles.success} className="fade-in scale-in-bounce">
          <span style={styles.successIcon} className="success-checkmark">✓</span>
          <span>{fileName} uploaded successfully!</span>
        </div>
      )}
      
      {error && (
        <div style={styles.error} className="fade-in error-shake">
          <span style={styles.errorIcon}>⚠️</span>
          <span>{error}</span>
        </div>
      )}
      
      <p style={styles.helpText}>
        Supported formats: MP3, WAV, OGG, M4A (Max 10MB)
      </p>
    </div>
  );
};

const styles = {
  container: {
    margin: '20px 0',
    textAlign: 'center'
  },
  uploadButton: {
    display: 'inline-block',
    padding: '12px 24px',
    backgroundColor: '#4CAF50',
    color: 'white',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '16px',
    fontWeight: '500',
    transition: 'all 0.3s ease',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    border: 'none'
  },
  buttonContent: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px'
  },
  icon: {
    fontSize: '20px'
  },
  progressBar: {
    width: '100%',
    maxWidth: '400px',
    height: '8px',
    backgroundColor: '#e0e0e0',
    borderRadius: '4px',
    margin: '12px auto',
    overflow: 'hidden'
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#4CAF50',
    transition: 'width 0.3s ease',
    borderRadius: '4px'
  },
  success: {
    marginTop: '12px',
    padding: '12px',
    backgroundColor: '#e8f5e9',
    color: '#2e7d32',
    borderRadius: '6px',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    justifyContent: 'center',
    maxWidth: '400px',
    margin: '12px auto'
  },
  successIcon: {
    fontSize: '18px',
    fontWeight: 'bold'
  },
  error: {
    marginTop: '12px',
    padding: '12px',
    backgroundColor: '#ffebee',
    color: '#c62828',
    borderRadius: '6px',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    justifyContent: 'center'
  },
  errorIcon: {
    fontSize: '18px'
  },
  helpText: {
    marginTop: '8px',
    fontSize: '13px',
    color: '#666',
    fontStyle: 'italic'
  }
};

export default VoiceFileUpload;
