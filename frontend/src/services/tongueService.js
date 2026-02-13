/**
 * Tongue Service - Direct Tongue Analysis
 * Provides tongue image analysis and explainability
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

class TongueService {
  /**
   * Analyze tongue image
   */
  async analyzeTongue(imageFile) {
    try {
      const formData = new FormData();
      formData.append('file', imageFile);
      
      const response = await fetch(`${API_BASE_URL}/tongue/analyze`, {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        throw new Error('Failed to analyze tongue image');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error analyzing tongue:', error);
      throw error;
    }
  }
  
  /**
   * Get explainability for tongue analysis
   */
  async explainAnalysis(imageFile) {
    try {
      const formData = new FormData();
      formData.append('file', imageFile);
      
      const response = await fetch(`${API_BASE_URL}/tongue/explain`, {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        throw new Error('Failed to get tongue analysis explanation');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error getting tongue explanation:', error);
      throw error;
    }
  }
}

export default new TongueService();
