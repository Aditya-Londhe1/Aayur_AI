/**
 * Voice Service - Advanced Voice Processing Features
 * Provides speech-to-text, text-to-speech, and voice consultation
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

class VoiceService {
  /**
   * Convert speech to text
   */
  async speechToText(audioFile, language = 'en') {
    try {
      const formData = new FormData();
      formData.append('audio_file', audioFile);
      formData.append('language', language);
      
      const response = await fetch(`${API_BASE_URL}/voice/speech-to-text`, {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        throw new Error('Failed to convert speech to text');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error in speech-to-text:', error);
      throw error;
    }
  }
  
  /**
   * Convert text to speech
   */
  async textToSpeech(text, language = 'en', voiceType = 'female') {
    try {
      const formData = new FormData();
      formData.append('text', text);
      formData.append('language', language);
      formData.append('voice_type', voiceType);
      
      const response = await fetch(`${API_BASE_URL}/voice/text-to-speech`, {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        throw new Error('Failed to convert text to speech');
      }
      
      // Return audio blob
      const blob = await response.blob();
      return {
        success: true,
        audioBlob: blob,
        audioUrl: URL.createObjectURL(blob)
      };
    } catch (error) {
      console.error('Error in text-to-speech:', error);
      throw error;
    }
  }
  
  /**
   * Voice-guided consultation
   */
  async voiceConsultation(audioFile, language = 'en') {
    try {
      const formData = new FormData();
      formData.append('audio_file', audioFile);
      formData.append('language', language);
      
      const response = await fetch(`${API_BASE_URL}/voice/voice-consultation`, {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        throw new Error('Failed to process voice consultation');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error in voice consultation:', error);
      throw error;
    }
  }
  
  /**
   * Extract symptoms from voice input
   */
  async voiceSymptomInput(audioFile, language = 'en') {
    try {
      const formData = new FormData();
      formData.append('audio_file', audioFile);
      formData.append('language', language);
      
      const response = await fetch(`${API_BASE_URL}/voice/voice-symptoms`, {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        throw new Error('Failed to extract symptoms from voice');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error in voice symptom input:', error);
      throw error;
    }
  }
  
  /**
   * Extract symptoms from text
   */
  async extractSymptomsFromText(text, language = 'en') {
    try {
      const formData = new FormData();
      formData.append('text', text);
      formData.append('language', language);
      
      const response = await fetch(`${API_BASE_URL}/voice/extract-symptoms-from-text`, {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        throw new Error('Failed to extract symptoms from text');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error extracting symptoms from text:', error);
      throw error;
    }
  }
  
  /**
   * Get list of supported languages
   */
  async getSupportedLanguages() {
    try {
      const response = await fetch(`${API_BASE_URL}/voice/supported-languages`);
      
      if (!response.ok) {
        throw new Error('Failed to get supported languages');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error getting supported languages:', error);
      throw error;
    }
  }
  
  /**
   * Health check
   */
  async healthCheck() {
    try {
      const response = await fetch(`${API_BASE_URL}/voice/health`);
      return await response.json();
    } catch (error) {
      console.error('Error checking voice service health:', error);
      throw error;
    }
  }
}

export default new VoiceService();
