import React, { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import Home from './pages/Home'
import AssessmentEnhanced from './pages/AssessmentEnhanced'
import Results from './pages/Results'
import About from './pages/About'
import VerifyEmail from './pages/VerifyEmail'
import ForgotPassword from './pages/ForgotPassword'
import ResetPassword from './pages/ResetPassword'
import ConsultationHistory from './pages/ConsultationHistory'
import TranslationPage from './pages/TranslationPage'
import IncrementalConsultationPage from './pages/IncrementalConsultationPage'
import FeedbackPage from './pages/FeedbackPage'
import VoiceAssistant from './components/VoiceAssistant'
import Login from './components/Login'
import Register from './components/Register'
import UserProfile from './components/UserProfile'
import UserMenu from './components/UserMenu'
import ProtectedRoute from './components/ProtectedRoute'
import { t, getLanguages } from './i18n/translations'
import './App.css'
import './styles/animations.css'
import './styles/feedback.css'

function AppContent() {
  const [language, setLanguage] = useState('en')
  const { isAuthenticated } = useAuth()

  const languages = getLanguages()

  return (
    <div className="app">
      <nav className="navbar">
        <div className="nav-brand">
          <img src="/logo-small.png" alt="AayurAI Logo" className="logo-image" />
          <span className="logo-text">AayurAI</span>
          <span className="ai-badge">
            <svg className="ai-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M2 17L12 22L22 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M2 12L12 17L22 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            <span className="ai-text">AI-Powered</span>
          </span>
        </div>
        <div className="nav-links">
          <Link to="/">{t('nav.home', language)}</Link>
          {isAuthenticated && (
            <>
              <Link to="/assessment">{t('nav.assessment', language)}</Link>
              <Link to="/incremental-consultation" className="nav-link-with-icon">
                <svg className="nav-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M9 5H7C5.89543 5 5 5.89543 5 7V19C5 20.1046 5.89543 21 7 21H17C18.1046 21 19 20.1046 19 19V7C19 5.89543 18.1046 5 17 5H15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M9 5C9 3.89543 9.89543 3 11 3H13C14.1046 3 15 3.89543 15 5V7H9V5Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M9 12H15" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                  <path d="M9 16H15" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                </svg>
                Step-by-Step
              </Link>
              <Link to="/voice-assistant" className="nav-link-with-icon">
                <svg className="nav-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 1C10.3431 1 9 2.34315 9 4V12C9 13.6569 10.3431 15 12 15C13.6569 15 15 13.6569 15 12V4C15 2.34315 13.6569 1 12 1Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M19 10V12C19 15.866 15.866 19 12 19C8.13401 19 5 15.866 5 12V10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M12 19V23" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M8 23H16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                Voice AI
              </Link>
              <Link to="/translation" className="nav-link-with-icon">
                <svg className="nav-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M2 12H22" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M12 2C14.5013 4.73835 15.9228 8.29203 16 12C15.9228 15.708 14.5013 19.2616 12 22C9.49872 19.2616 8.07725 15.708 8 12C8.07725 8.29203 9.49872 4.73835 12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                Translation
              </Link>
              <Link to="/feedback" className="nav-link-with-icon">
                <svg className="nav-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M21 15C21 15.5304 20.7893 16.0391 20.4142 16.4142C20.0391 16.7893 19.5304 17 19 17H7L3 21V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H19C19.5304 3 20.0391 3.21071 20.4142 3.58579C20.7893 3.96086 21 4.46957 21 5V15Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M8 9H16" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                  <path d="M8 13H14" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                </svg>
                Feedback
              </Link>
            </>
          )}
          <Link to="/about">{t('nav.about', language)}</Link>
          <div className="language-selector">
            <select 
              value={language} 
              onChange={(e) => setLanguage(e.target.value)}
              className="language-dropdown"
            >
              {languages.map(lang => (
                <option key={lang.code} value={lang.code}>
                  {lang.flag} {lang.nativeName}
                </option>
              ))}
            </select>
          </div>
          {isAuthenticated ? (
            <UserMenu />
          ) : (
            <div className="auth-buttons">
              <Link to="/login" className="btn-secondary">Login</Link>
              <Link to="/register" className="btn-primary">Sign Up</Link>
            </div>
          )}
        </div>
      </nav>

      <main className="main-content">
        <Routes>
          <Route path="/" element={<Home language={language} />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/verify-email" element={<VerifyEmail />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password" element={<ResetPassword />} />
          <Route path="/about" element={<About language={language} />} />
          
          {/* Protected Routes */}
          <Route 
            path="/assessment" 
            element={
              <ProtectedRoute>
                <AssessmentEnhanced language={language} />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/voice-assistant" 
            element={
              <ProtectedRoute>
                <VoiceAssistant />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/results" 
            element={
              <ProtectedRoute>
                <Results language={language} />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/profile" 
            element={
              <ProtectedRoute>
                <UserProfile />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/history" 
            element={
              <ProtectedRoute>
                <ConsultationHistory />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/translation" 
            element={
              <ProtectedRoute>
                <TranslationPage />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/incremental-consultation" 
            element={
              <ProtectedRoute>
                <IncrementalConsultationPage language={language} />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/feedback" 
            element={
              <ProtectedRoute>
                <FeedbackPage />
              </ProtectedRoute>
            } 
          />
        </Routes>
      </main>

      <footer className="footer">
        <p>{t('footer.copyright', language)}</p>
        <p className="disclaimer">
          <svg className="footer-ai-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M2 17L12 22L22 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M2 12L12 17L22 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          Powered by Advanced AI: Deep Learning, Computer Vision, NLP & Signal Processing
        </p>
        <p className="disclaimer">
          {t('footer.disclaimer', language)}
        </p>
      </footer>
    </div>
  )
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </Router>
  )
}

export default App
