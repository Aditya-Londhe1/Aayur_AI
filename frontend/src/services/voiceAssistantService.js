/**
 * Voice Assistant API Service
 */

const API_BASE_URL = 'http://localhost:8000/api/v1';

class VoiceAssistantService {
  /**
   * Start a new conversation session
   */
  async startSession(language = 'en') {
    try {
      const response = await fetch(`${API_BASE_URL}/voice-assistant/start-session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ language }),
      });

      if (!response.ok) {
        throw new Error('Failed to start session');
      }

      return await response.json();
    } catch (error) {
      console.error('Error starting session:', error);
      throw error;
    }
  }

  /**
   * Send message and get AI response (Option A - supports both session_id and conversation_id)
   */
  async chat(sessionId, message, language = 'en') {
    try {
      console.log('API: Sending chat request:', { sessionId, message, language });
      
      const response = await fetch(`${API_BASE_URL}/voice-assistant/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          conversation_id: sessionId,  // Option A uses conversation_id
          message,
          language,
        }),
      });

      console.log('API: Response status:', response.status);
      console.log('API: Response ok:', response.ok);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('API: Error response:', errorText);
        throw new Error('Failed to send message');
      }

      const data = await response.json();
      console.log('API: Response data:', data);
      
      return data;
    } catch (error) {
      console.error('API: Error in chat:', error);
      throw error;
    }
  }

  /**
   * Get session information
   */
  async getSession(sessionId) {
    try {
      const response = await fetch(`${API_BASE_URL}/voice-assistant/session/${sessionId}`);

      if (!response.ok) {
        throw new Error('Failed to get session');
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting session:', error);
      throw error;
    }
  }

  /**
   * End conversation session
   */
  async endSession(sessionId) {
    try {
      const response = await fetch(`${API_BASE_URL}/voice-assistant/session/${sessionId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to end session');
      }

      return await response.json();
    } catch (error) {
      console.error('Error ending session:', error);
      throw error;
    }
  }

  /**
   * Detect language of text
   */
  async detectLanguage(text) {
    try {
      const response = await fetch(`${API_BASE_URL}/voice-assistant/detect-language?text=${encodeURIComponent(text)}`);

      if (!response.ok) {
        throw new Error('Failed to detect language');
      }

      return await response.json();
    } catch (error) {
      console.error('Error detecting language:', error);
      throw error;
    }
  }

  /**
   * Upload voice file for processing (Option A)
   */
  async uploadVoice(audioFile, conversationId = null, language = null) {
    try {
      const formData = new FormData();
      formData.append('audio', audioFile);
      if (conversationId) formData.append('conversation_id', conversationId);
      if (language) formData.append('language', language);
      
      const response = await fetch(`${API_BASE_URL}/voice-assistant/upload-voice`, {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        throw new Error('Failed to upload voice file');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error uploading voice:', error);
      throw error;
    }
  }

  /**
   * Translate text between languages
   */
  async translate(text, targetLanguage, sourceLanguage = null) {
    try {
      const response = await fetch(`${API_BASE_URL}/voice-assistant/translate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          text,
          target_language: targetLanguage,
          source_language: sourceLanguage
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to translate text');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error translating:', error);
      throw error;
    }
  }

  /**
   * Get conversation details (Option A)
   */
  async getConversation(conversationId) {
    try {
      const response = await fetch(`${API_BASE_URL}/voice-assistant/conversation/${conversationId}`);
      
      if (!response.ok) {
        throw new Error('Failed to get conversation');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error getting conversation:', error);
      throw error;
    }
  }

  /**
   * End conversation (Option A)
   */
  async endConversation(conversationId) {
    try {
      const response = await fetch(`${API_BASE_URL}/voice-assistant/conversation/${conversationId}`, {
        method: 'DELETE'
      });
      
      if (!response.ok) {
        throw new Error('Failed to end conversation');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error ending conversation:', error);
      throw error;
    }
  }
}

export default new VoiceAssistantService();
