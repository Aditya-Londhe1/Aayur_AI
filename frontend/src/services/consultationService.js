/**
 * Consultation Service - Incremental Consultation Flow
 * Provides step-by-step consultation building
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

class ConsultationService {
  /**
   * Create a new consultation
   */
  async createConsultation(patientData) {
    try {
      const formData = new FormData();
      formData.append('patient_name', patientData.name);
      formData.append('age', patientData.age);
      formData.append('gender', patientData.gender);
      
      const response = await fetch(`${API_BASE_URL}/consultations/create`, {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        throw new Error('Failed to create consultation');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error creating consultation:', error);
      throw error;
    }
  }
  
  /**
   * Add tongue analysis to consultation
   */
  async addTongueAnalysis(consultationId, tongueImage) {
    try {
      const formData = new FormData();
      formData.append('tongue_image', tongueImage);
      
      const response = await fetch(`${API_BASE_URL}/consultations/${consultationId}/add-tongue`, {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        throw new Error('Failed to add tongue analysis');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error adding tongue analysis:', error);
      throw error;
    }
  }
  
  /**
   * Add pulse analysis to consultation
   */
  async addPulseAnalysis(consultationId, pulseData) {
    try {
      const formData = new FormData();
      formData.append('pulse_data', JSON.stringify(pulseData));
      
      const response = await fetch(`${API_BASE_URL}/consultations/${consultationId}/add-pulse`, {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        throw new Error('Failed to add pulse analysis');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error adding pulse analysis:', error);
      throw error;
    }
  }
  
  /**
   * Add symptoms to consultation
   */
  async addSymptoms(consultationId, symptoms) {
    try {
      const formData = new FormData();
      formData.append('symptoms', JSON.stringify(symptoms));
      
      const response = await fetch(`${API_BASE_URL}/consultations/${consultationId}/add-symptoms`, {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        throw new Error('Failed to add symptoms');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error adding symptoms:', error);
      throw error;
    }
  }
  
  /**
   * Generate final report for consultation
   */
  async generateReport(consultationId) {
    try {
      const response = await fetch(`${API_BASE_URL}/consultations/${consultationId}/generate-report`, {
        method: 'POST'
      });
      
      if (!response.ok) {
        throw new Error('Failed to generate report');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error generating report:', error);
      throw error;
    }
  }
  
  /**
   * Complete consultation (all-in-one endpoint)
   */
  async completeConsultation(consultationData) {
    try {
      const formData = new FormData();
      
      // Patient info
      formData.append('patient_name', consultationData.name);
      formData.append('age', consultationData.age);
      formData.append('gender', consultationData.gender);
      
      // Symptoms
      if (consultationData.symptoms && consultationData.symptoms.length > 0) {
        formData.append('symptoms', JSON.stringify(consultationData.symptoms));
      }
      
      // Pulse data
      if (consultationData.pulseData) {
        formData.append('pulse_data', JSON.stringify(consultationData.pulseData));
      }
      
      // Tongue image
      if (consultationData.tongueImage) {
        formData.append('tongue_image', consultationData.tongueImage);
      }
      
      // Voice audio
      if (consultationData.voiceAudio) {
        formData.append('voice_audio', consultationData.voiceAudio);
      }
      
      // Locale
      formData.append('locale', consultationData.locale || 'en');
      
      const response = await fetch(`${API_BASE_URL}/consultations/complete`, {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        throw new Error('Failed to complete consultation');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error completing consultation:', error);
      throw error;
    }
  }
  
  /**
   * Health check
   */
  async healthCheck() {
    try {
      const response = await fetch(`${API_BASE_URL}/consultations/health`);
      return await response.json();
    } catch (error) {
      console.error('Error checking consultation service health:', error);
      throw error;
    }
  }
}

export default new ConsultationService();
