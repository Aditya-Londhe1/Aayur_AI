import React from 'react'
import { Link } from 'react-router-dom'
import { t } from '../i18n/translations'

function Home({ language }) {
  return (
    <div className="home-page fade-in">
      <div className="hero">
        <div className="hero-logo">
          <img src="/logo.png" alt="AayurAI Logo" className="hero-logo-image" />
        </div>
        <div className="ai-badge-large">
          <span className="ai-icon">🤖</span>
          <span>{t('home.ai_powered', language)}</span>
        </div>
        <h1>{t('home.title', language)}</h1>
        <p>{t('home.subtitle', language)}</p>
        <Link to="/assessment" className="btn btn-primary">
          <span className="ai-icon">🤖</span>
          {t('home.start', language)}
        </Link>
      </div>

      <div className="ai-tech-banner">
        <h3>🧠 {t('home.ai_tech', language)}</h3>
        <div className="tech-badges">
          <span className="tech-badge">🧠 Deep Learning</span>
          <span className="tech-badge">👁️ Computer Vision</span>
          <span className="tech-badge">💬 Natural Language Processing</span>
          <span className="tech-badge">📊 Signal Processing</span>
          <span className="tech-badge">🔗 Multi-Modal Fusion</span>
        </div>
      </div>

      <div className="features">
        <div className="feature-card">
          <div className="feature-icon">👁️</div>
          <div className="ai-indicator">AI-Powered</div>
          <h3>{t('feature.tongue', language)}</h3>
          <p>{t('feature.tongue.desc', language)}</p>
          <div className="tech-detail">
            <small>🤖 ResNet Architecture • Grad-CAM Explainability</small>
          </div>
        </div>

        <div className="feature-card">
          <div className="feature-icon">💓</div>
          <div className="ai-indicator">AI-Powered</div>
          <h3>{t('feature.pulse', language)}</h3>
          <p>{t('feature.pulse.desc', language)}</p>
          <div className="tech-detail">
            <small>🤖 HRV Analysis • Frequency Domain Processing</small>
          </div>
        </div>

        <div className="feature-card">
          <div className="feature-icon">📝</div>
          <div className="ai-indicator">AI-Powered</div>
          <h3>{t('feature.symptoms', language)}</h3>
          <p>{t('feature.symptoms.desc', language)}</p>
          <div className="tech-detail">
            <small>🤖 BERT Models • Semantic Analysis</small>
          </div>
        </div>

        <div className="feature-card">
          <div className="feature-icon">🎤</div>
          <div className="ai-indicator">AI-Powered</div>
          <h3>{t('feature.voice', language)}</h3>
          <p>{t('feature.voice.desc', language)}</p>
          <div className="tech-detail">
            <small>🤖 Audio Processing • Feature Extraction</small>
          </div>
        </div>

        <div className="feature-card">
          <div className="feature-icon">🧘</div>
          <div className="ai-indicator">AI-Powered</div>
          <h3>{t('feature.personalized', language)}</h3>
          <p>{t('feature.personalized.desc', language)}</p>
          <div className="tech-detail">
            <small>🤖 Recommendation Engine • Personalization AI</small>
          </div>
        </div>

        <div className="feature-card">
          <div className="feature-icon">🧠</div>
          <div className="ai-indicator">AI-Powered</div>
          <h3>{t('feature.explainable', language)}</h3>
          <p>{t('feature.explainable.desc', language)}</p>
          <div className="tech-detail">
            <small>🤖 XAI • Confidence Scoring • Interpretability</small>
          </div>
        </div>
      </div>

      <div className="card text-center">
        <h2>🤖 {t('home.how_works', language)}</h2>
        <div className="grid grid-3 mt-4">
          <div>
            <div className="feature-icon">1️⃣</div>
            <h3>{t('home.data_collection', language)}</h3>
            <p>{t('home.data_collection_desc', language)}</p>
          </div>
          <div>
            <div className="feature-icon">2️⃣</div>
            <h3>{t('home.ai_analysis', language)}</h3>
            <p>{t('home.ai_analysis_desc', language)}</p>
          </div>
          <div>
            <div className="feature-icon">3️⃣</div>
            <h3>{t('home.intelligent_results', language)}</h3>
            <p>{t('home.intelligent_results_desc', language)}</p>
          </div>
        </div>
      </div>

      <div className="ai-confidence-section">
        <h2>🎯 AI Confidence & Accuracy</h2>
        <div className="grid grid-2 mt-3">
          <div className="confidence-card">
            <h3>Transparent AI</h3>
            <p>Every diagnosis includes confidence scores showing AI certainty levels</p>
            <div className="confidence-example">
              <div className="confidence-bar">
                <div className="confidence-fill" style={{width: '85%'}}>85%</div>
              </div>
              <small>Example: High confidence diagnosis</small>
            </div>
          </div>
          <div className="confidence-card">
            <h3>Validated Models</h3>
            <p>AI models trained on extensive datasets and validated by Ayurvedic experts</p>
            <ul style={{textAlign: 'left', marginTop: '1rem'}}>
              <li>✓ Expert-validated algorithms</li>
              <li>✓ Continuous learning</li>
              <li>✓ Regular accuracy testing</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Doctor Testimonials Section - Real Survey Data */}
      <div className="testimonials-section">
        <h2>👨‍⚕️ What Doctors Say</h2>
        <p className="section-subtitle">Real feedback from verified Ayurvedic practitioners</p>
        
        <div className="testimonials-grid">
          {/* Dr. Vinay Ramrao Gidage - 10/10 Rating */}
          <div className="testimonial-card">
            <div className="testimonial-header">
              <div className="doctor-avatar">
                <span>👨‍⚕️</span>
              </div>
              <div className="doctor-info">
                <h4>Dr. Vinay Ramrao Gidage</h4>
                <p>BHMS, CCH, CGO</p>
                <p className="doctor-location">Private Clinic • 11-20 years experience</p>
              </div>
            </div>
            <div className="testimonial-rating">
              ⭐⭐⭐⭐⭐ <span className="rating-score">10/10</span>
            </div>
            <p className="testimonial-text">
              "Preventive Ayurveda is crucial in today's healthcare, and AAYUR AI addresses this perfectly. The explainable AI feature that shows reasoning behind diagnoses is exactly what practitioners need. I would definitely use this in my practice and recommend it for Ministry of AYUSH programs."
            </p>
            <div className="testimonial-footer">
              <span className="testimonial-badge">✓ Would use in practice</span>
              <span className="testimonial-badge">Diet recommendations</span>
            </div>
          </div>

          {/* Dr. Shreyas Avinash Jadhav - 10/10 Rating */}
          <div className="testimonial-card">
            <div className="testimonial-header">
              <div className="doctor-avatar">
                <span>👨‍⚕️</span>
              </div>
              <div className="doctor-info">
                <h4>Dr. Shreyas Avinash Jadhav</h4>
                <p>BAMS, MS</p>
                <p className="doctor-location">Hospital • 6-10 years experience</p>
              </div>
            </div>
            <div className="testimonial-rating">
              ⭐⭐⭐⭐⭐ <span className="rating-score">10/10</span>
            </div>
            <p className="testimonial-text">
              "AI is incredibly useful for Ayurveda! The system's ability to analyze tongue, pulse, and symptoms digitally is a game-changer. The explainable AI approach builds trust and helps in early awareness and screening. Adding AI monitoring would make it even more powerful for continuous patient care."
            </p>
            <div className="testimonial-footer">
              <span className="testimonial-badge">✓ Strongly supports AI in Ayurveda</span>
              <span className="testimonial-badge">Suggests: AI monitoring</span>
            </div>
          </div>

          {/* Dr. Fathima Stephen Sharma - 9/10 Rating */}
          <div className="testimonial-card">
            <div className="testimonial-header">
              <div className="doctor-avatar">
                <span>👩‍⚕️</span>
              </div>
              <div className="doctor-info">
                <h4>Dr. Fathima Stephen Sharma</h4>
                <p>BAMS, MD (Panchkarma)</p>
                <p className="doctor-location">Hospital • 6-10 years Panchkarma experience</p>
              </div>
            </div>
            <div className="testimonial-rating">
              ⭐⭐⭐⭐⭐ <span className="rating-score">9/10</span>
            </div>
            <p className="testimonial-text">
              "As a Panchkarma specialist, I see immense value in this AI-based wellness system. The personalized diet and lifestyle advice feature is particularly important for patient care. This technology is especially needed in government hospitals where resources are limited. Highly recommended for AYUSH programs."
            </p>
            <div className="testimonial-footer">
              <span className="testimonial-badge">✓ Panchkarma Specialist</span>
              <span className="testimonial-badge">Focus: Govt hospitals</span>
            </div>
          </div>

          {/* Dr. Vaibhav Datir - 8/10 Rating */}
          <div className="testimonial-card">
            <div className="testimonial-header">
              <div className="doctor-avatar">
                <span>👨‍⚕️</span>
              </div>
              <div className="doctor-info">
                <h4>Dr. Vaibhav Datir</h4>
                <p>B.A.M.S (General)</p>
                <p className="doctor-location">Hospital • 0-5 years experience</p>
              </div>
            </div>
            <div className="testimonial-rating">
              ⭐⭐⭐⭐ <span className="rating-score">8/10</span>
            </div>
            <p className="testimonial-text">
              "The comprehensive approach of AAYUR AI is impressive. Digital analysis of tongue, pulse, and symptoms combined with personalized diet advice, dosha imbalance detection, and multilingual voice support makes it accessible and practical. This can definitely help in early awareness and screening."
            </p>
            <div className="testimonial-footer">
              <span className="testimonial-badge">✓ Supports digital analysis</span>
              <span className="testimonial-badge">Values: Multilingual support</span>
            </div>
          </div>
        </div>

        {/* Survey Statistics */}
        <div className="survey-stats">
          <h3>Survey Highlights</h3>
          <div className="stats-grid">
            <div className="stat-item">
              <div className="stat-number">9.25/10</div>
              <div className="stat-label">Average Rating</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">100%</div>
              <div className="stat-label">Would Use in Practice</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">100%</div>
              <div className="stat-label">Recommend for AYUSH</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">75%</div>
              <div className="stat-label">Support Digital Analysis</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Home
