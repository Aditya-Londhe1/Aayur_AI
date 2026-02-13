/**
 * Pulse Service - Direct Pulse Analysis
 * Provides pulse generation, validation, and analysis
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

class PulseService {
  /**
   * Generate synthetic pulse data from heart rate
   */
  async generateSyntheticPulse(heartRate, duration = 30) {
    try {
      const formData = new FormData();
      formData.append('heart_rate', heartRate);
      formData.append('duration', duration);
      
      const response = await fetch(`${API_BASE_URL}/pulse/generate-synthetic-pulse`, {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        throw new Error('Failed to generate synthetic pulse');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error generating synthetic pulse:', error);
      throw error;
    }
  }
  
  /**
   * Validate pulse data format and quality
   */
  async validatePulseData(pulseData) {
    try {
      const formData = new FormData();
      formData.append('pulse_data', JSON.stringify(pulseData));
      
      const response = await fetch(`${API_BASE_URL}/pulse/validate-pulse-data`, {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        throw new Error('Failed to validate pulse data');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error validating pulse data:', error);
      throw error;
    }
  }
  
  /**
   * Get sensor integration guide
   */
  async getSensorIntegrationGuide() {
    try {
      const response = await fetch(`${API_BASE_URL}/pulse/sensor-integration-guide`);
      
      if (!response.ok) {
        throw new Error('Failed to get sensor integration guide');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error getting sensor integration guide:', error);
      throw error;
    }
  }
  
  /**
   * Health check
   */
  async healthCheck() {
    try {
      const response = await fetch(`${API_BASE_URL}/pulse/health`);
      return await response.json();
    } catch (error) {
      console.error('Error checking pulse service health:', error);
      throw error;
    }
  }
}

export default new PulseService();
