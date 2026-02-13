/**
 * Feedback Service
 * Handles user feedback and testimonials
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

class FeedbackService {
  /**
   * Submit new feedback
   */
  async submitFeedback(feedbackData) {
    try {
      const token = localStorage.getItem('access_token');
      
      const response = await fetch(`${API_BASE_URL}/feedback/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(feedbackData)
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to submit feedback');
      }

      return await response.json();
    } catch (error) {
      console.error('Error submitting feedback:', error);
      throw error;
    }
  }

  /**
   * Get user's own feedback
   */
  async getMyFeedback() {
    try {
      const token = localStorage.getItem('access_token');
      
      const response = await fetch(`${API_BASE_URL}/feedback/my-feedback`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch feedback');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching feedback:', error);
      throw error;
    }
  }

  /**
   * Get recent positive feedback (public)
   */
  async getRecentFeedback(limit = 10, minRating = 4.0) {
    try {
      const response = await fetch(
        `${API_BASE_URL}/feedback/recent?limit=${limit}&min_rating=${minRating}`
      );

      if (!response.ok) {
        throw new Error('Failed to fetch recent feedback');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching recent feedback:', error);
      throw error;
    }
  }

  /**
   * Get feedback statistics (public)
   */
  async getFeedbackStats() {
    try {
      const response = await fetch(`${API_BASE_URL}/feedback/stats`);

      if (!response.ok) {
        throw new Error('Failed to fetch feedback stats');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching feedback stats:', error);
      throw error;
    }
  }

  /**
   * Delete own feedback
   */
  async deleteFeedback(feedbackId) {
    try {
      const token = localStorage.getItem('access_token');
      
      const response = await fetch(`${API_BASE_URL}/feedback/${feedbackId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to delete feedback');
      }

      return true;
    } catch (error) {
      console.error('Error deleting feedback:', error);
      throw error;
    }
  }
}

export default new FeedbackService();
