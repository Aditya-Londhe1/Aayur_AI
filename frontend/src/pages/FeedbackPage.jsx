/**
 * Feedback Page
 * Allows users to submit feedback and view their past feedback
 */

import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import feedbackService from '../services/feedbackService';

const FeedbackPage = () => {
  const { user } = useAuth();
  const [rating, setRating] = useState(0);
  const [hoverRating, setHoverRating] = useState(0);
  const [title, setTitle] = useState('');
  const [message, setMessage] = useState('');
  const [category, setCategory] = useState('general');
  const [myFeedback, setMyFeedback] = useState([]);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadMyFeedback();
  }, []);

  const loadMyFeedback = async () => {
    try {
      setLoading(true);
      const feedback = await feedbackService.getMyFeedback();
      setMyFeedback(feedback);
    } catch (err) {
      console.error('Failed to load feedback:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (rating === 0) {
      setError('Please select a rating');
      return;
    }

    if (message.length < 10) {
      setError('Please provide at least 10 characters of feedback');
      return;
    }

    try {
      setSubmitting(true);
      setError('');
      
      await feedbackService.submitFeedback({
        rating,
        title: title || null,
        message,
        category
      });

      setSuccess(true);
      setRating(0);
      setTitle('');
      setMessage('');
      setCategory('general');
      
      // Reload feedback list
      await loadMyFeedback();

      // Hide success message after 3 seconds
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(err.message || 'Failed to submit feedback');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (feedbackId) => {
    if (!confirm('Are you sure you want to delete this feedback?')) {
      return;
    }

    try {
      await feedbackService.deleteFeedback(feedbackId);
      await loadMyFeedback();
    } catch (err) {
      alert('Failed to delete feedback');
    }
  };

  const renderStars = (currentRating, isInteractive = false) => {
    return (
      <div className="star-rating">
        {[1, 2, 3, 4, 5].map((star) => (
          <span
            key={star}
            className={`star ${star <= (isInteractive ? (hoverRating || rating) : currentRating) ? 'filled' : ''}`}
            onClick={() => isInteractive && setRating(star)}
            onMouseEnter={() => isInteractive && setHoverRating(star)}
            onMouseLeave={() => isInteractive && setHoverRating(0)}
            style={{ cursor: isInteractive ? 'pointer' : 'default' }}
          >
            ★
          </span>
        ))}
      </div>
    );
  };

  return (
    <div className="feedback-page">
      <div className="feedback-header">
        <h1>📝 Share Your Feedback</h1>
        <p>Help us improve AayurAI with your valuable feedback</p>
      </div>

      <div className="feedback-container">
        {/* Feedback Form */}
        <div className="feedback-form-card">
          <h2>Submit New Feedback</h2>
          
          {success && (
            <div className="alert alert-success">
              ✅ Thank you for your feedback! We appreciate your input.
            </div>
          )}

          {error && (
            <div className="alert alert-error">
              ⚠️ {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Rating *</label>
              {renderStars(rating, true)}
              <small>Click to rate from 1 to 5 stars</small>
            </div>

            <div className="form-group">
              <label>Category</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="form-control"
              >
                <option value="general">General Feedback</option>
                <option value="accuracy">Diagnosis Accuracy</option>
                <option value="ui">User Interface</option>
                <option value="service">Customer Service</option>
                <option value="features">Feature Request</option>
                <option value="bug">Bug Report</option>
              </select>
            </div>

            <div className="form-group">
              <label>Title (Optional)</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Brief summary of your feedback"
                maxLength={200}
                className="form-control"
              />
            </div>

            <div className="form-group">
              <label>Your Feedback *</label>
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Please share your experience with AayurAI..."
                rows={6}
                minLength={10}
                maxLength={2000}
                required
                className="form-control"
              />
              <small>{message.length}/2000 characters</small>
            </div>

            <button
              type="submit"
              className="btn-primary btn-large"
              disabled={submitting}
            >
              {submitting ? '⏳ Submitting...' : '📤 Submit Feedback'}
            </button>
          </form>
        </div>

        {/* My Feedback History */}
        <div className="my-feedback-card">
          <h2>My Feedback History</h2>
          
          {loading ? (
            <div className="loading-state">
              <div className="loading-spinner"></div>
              <p>Loading your feedback...</p>
            </div>
          ) : myFeedback.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">📭</div>
              <p>You haven't submitted any feedback yet</p>
            </div>
          ) : (
            <div className="feedback-list">
              {myFeedback.map((feedback) => (
                <div key={feedback.id} className="feedback-item">
                  <div className="feedback-item-header">
                    <div>
                      {renderStars(feedback.rating)}
                      <span className="feedback-category">{feedback.category}</span>
                    </div>
                    <button
                      onClick={() => handleDelete(feedback.id)}
                      className="btn-delete-small"
                      title="Delete feedback"
                    >
                      🗑️
                    </button>
                  </div>
                  
                  {feedback.title && (
                    <h4 className="feedback-title">{feedback.title}</h4>
                  )}
                  
                  <p className="feedback-message">{feedback.message}</p>
                  
                  <div className="feedback-date">
                    {new Date(feedback.created_at).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default FeedbackPage;
