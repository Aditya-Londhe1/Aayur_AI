/**
 * Authentication Service
 * Handles all authentication-related API calls
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

class AuthService {
  /**
   * Register a new user
   */
  async register(userData) {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || data.message || 'Registration failed');
    }

    return data;
  }

  /**
   * Login user
   */
  async login(email, password) {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || 'Login failed');
    }

    // Store tokens
    this.setTokens(data.access_token, data.refresh_token);

    return data;
  }

  /**
   * Logout user
   */
  async logout() {
    const token = this.getAccessToken();

    if (token) {
      try {
        await fetch(`${API_BASE_URL}/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
      } catch (error) {
        console.error('Logout error:', error);
      }
    }

    // Clear tokens
    this.clearTokens();
  }

  /**
   * Get current user
   */
  async getCurrentUser() {
    const token = this.getAccessToken();

    if (!token) {
      throw new Error('No access token');
    }

    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    const data = await response.json();

    if (!response.ok) {
      if (response.status === 401) {
        // Token expired, try to refresh
        const refreshed = await this.refreshToken();
        if (refreshed) {
          return this.getCurrentUser();
        }
      }
      throw new Error(data.detail || 'Failed to get user');
    }

    return data;
  }

  /**
   * Update user profile
   */
  async updateProfile(profileData) {
    const token = this.getAccessToken();

    if (!token) {
      throw new Error('No access token');
    }

    const response = await fetch(`${API_BASE_URL}/users/me`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(profileData),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || 'Failed to update profile');
    }

    return data.user;
  }

  /**
   * Change password
   */
  async changePassword(currentPassword, newPassword) {
    const token = this.getAccessToken();

    if (!token) {
      throw new Error('No access token');
    }

    const response = await fetch(`${API_BASE_URL}/auth/change-password`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || 'Failed to change password');
    }

    return data;
  }

  /**
   * Refresh access token
   */
  async refreshToken() {
    const refreshToken = this.getRefreshToken();

    if (!refreshToken) {
      return false;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      const data = await response.json();

      if (!response.ok) {
        this.clearTokens();
        return false;
      }

      // Update tokens
      this.setTokens(data.access_token, data.refresh_token);
      return true;
    } catch (error) {
      console.error('Token refresh error:', error);
      this.clearTokens();
      return false;
    }
  }

  /**
   * Store tokens in localStorage
   */
  setTokens(accessToken, refreshToken) {
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
  }

  /**
   * Get access token from localStorage
   */
  getAccessToken() {
    return localStorage.getItem('access_token');
  }

  /**
   * Get refresh token from localStorage
   */
  getRefreshToken() {
    return localStorage.getItem('refresh_token');
  }

  /**
   * Clear tokens from localStorage
   */
  clearTokens() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated() {
    return !!this.getAccessToken();
  }

  /**
   * Make authenticated API request
   */
  async authenticatedRequest(url, options = {}) {
    const token = this.getAccessToken();

    if (!token) {
      throw new Error('No access token');
    }

    const headers = {
      ...options.headers,
      'Authorization': `Bearer ${token}`,
    };

    const response = await fetch(url, {
      ...options,
      headers,
    });

    // If unauthorized, try to refresh token
    if (response.status === 401) {
      const refreshed = await this.refreshToken();
      if (refreshed) {
        // Retry request with new token
        const newToken = this.getAccessToken();
        headers.Authorization = `Bearer ${newToken}`;
        return fetch(url, { ...options, headers });
      }
    }

    return response;
  }

  /**
   * Deactivate account (temporary suspension)
   */
  async deactivateAccount() {
    try {
      const token = this.getAccessToken();
      if (!token) {
        throw new Error('Not authenticated');
      }
      
      const response = await fetch(`${API_BASE_URL}/users/me/deactivate`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to deactivate account');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error deactivating account:', error);
      throw error;
    }
  }

  /**
   * Get user by ID (admin function)
   */
  async getUserById(userId) {
    try {
      const token = this.getAccessToken();
      if (!token) {
        throw new Error('Not authenticated');
      }
      
      const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to get user');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error getting user:', error);
      throw error;
    }
  }
}

export default new AuthService();
