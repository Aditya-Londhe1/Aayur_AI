/**
 * Symptom Service - Direct Symptom Analysis
 * Provides symptom analysis and text-based symptom extraction
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

class SymptomService {
  /**
   * Analyze symptoms directly
   */
  async analyzeSymptoms(symptoms, locale = 'en') {
    try {
      const response = await fetch(`${API_BASE_URL}/symptoms/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          symptoms,
          locale
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to analyze symptoms');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error analyzing symptoms:', error);
      throw error;
    }
  }
  
  /**
   * Analyze symptoms from text description
   */
  async analyzeSymptomsText(text, locale = 'en') {
    try {
      const response = await fetch(`${API_BASE_URL}/symptoms/analyze-text`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          text,
          locale
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to analyze symptoms from text');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error analyzing symptoms from text:', error);
      throw error;
    }
  }
  
  /**
   * Health check
   */
  async healthCheck() {
    try {
      const response = await fetch(`${API_BASE_URL}/symptoms/health`);
      return await response.json();
    } catch (error) {
      console.error('Error checking symptom service health:', error);
      throw error;
    }
  }
}

export default new SymptomService();
