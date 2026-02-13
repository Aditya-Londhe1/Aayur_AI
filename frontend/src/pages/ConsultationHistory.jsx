/**
 * Consultation History Page
 * Shows recent assessments and allows downloading reports
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const ConsultationHistory = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [consultations, setConsultations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [downloadingId, setDownloadingId] = useState(null);

  useEffect(() => {
    loadConsultations();
  }, []);

  const loadConsultations = () => {
    try {
      // Load consultations from localStorage
      const stored = localStorage.getItem('consultation_history');
      if (stored) {
        const history = JSON.parse(stored);
        // Sort by date, newest first
        const sorted = history.sort((a, b) => 
          new Date(b.timestamp) - new Date(a.timestamp)
        );
        setConsultations(sorted);
      }
    } catch (error) {
      console.error('Failed to load consultations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleViewResults = (consultation) => {
    // Navigate to results with the consultation data
    // Add fromHistory flag to prevent duplicate saving
    navigate('/results', { 
      state: { 
        result: {
          diagnosis: consultation.data,
          recommendations: consultation.data.recommendations,
          confidence: consultation.data.confidence,
          analyses: {
            pulse: consultation.data.pulse_analysis,
            tongue: consultation.data.tongue_analysis,
            symptoms: consultation.data.symptom_analysis
          }
        },
        patientInfo: consultation.patientInfo || consultation.data.patient_info,
        fromHistory: true  // Flag to prevent duplicate saving
      } 
    });
  };

  const handleDownloadPDF = async (consultation) => {
    try {
      setDownloadingId(consultation.id);
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        alert('Please login to download PDF reports');
        setDownloadingId(null);
        return;
      }
      
      // Format the data properly for PDF generation
      const pdfData = {
        primary_dosha: consultation.data.primary_dosha,
        imbalance_level: consultation.data.imbalance_level,
        confidence: consultation.data.confidence,
        dosha_scores: consultation.data.dosha_scores,
        pulse_analysis: consultation.data.pulse_analysis,
        tongue_analysis: consultation.data.tongue_analysis,
        symptom_analysis: consultation.data.symptom_analysis,
        fusion_details: consultation.data.fusion_details,
        recommendations: consultation.data.recommendations,
        home_remedies: consultation.data.home_remedies,
        patient_info: consultation.data.patient_info || consultation.patientInfo,
        prakriti_type: consultation.data.prakriti_type,
        vikriti_type: consultation.data.vikriti_type,
        explanation: consultation.data.explanation,
        likely_conditions: consultation.data.likely_conditions
      };
      
      console.log('Sending PDF data:', pdfData);
      
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'}/diagnosis/generate-pdf`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(pdfData),
      });

      if (response.ok) {
        // Download the PDF
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `AayurAI_Report_${new Date(consultation.timestamp).toISOString().split('T')[0]}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        console.log('✅ PDF downloaded successfully');
      } else {
        const errorText = await response.text();
        console.error('PDF generation failed:', errorText);
        
        let errorMessage = 'Failed to generate PDF report';
        try {
          const errorJson = JSON.parse(errorText);
          errorMessage = errorJson.detail || errorMessage;
        } catch (e) {
          // Use default message
        }
        
        alert(`${errorMessage}\n\nStatus: ${response.status} ${response.statusText}`);
      }
    } catch (error) {
      console.error('Failed to download PDF:', error);
      alert(`Failed to download PDF report: ${error.message}\n\nPlease make sure the backend server is running.`);
    } finally {
      setDownloadingId(null);
    }
  };

  const handleDeleteConsultation = (id) => {
    if (confirm('Are you sure you want to delete this consultation?')) {
      const updated = consultations.filter(c => c.id !== id);
      setConsultations(updated);
      localStorage.setItem('consultation_history', JSON.stringify(updated));
    }
  };

  const getDoshaColor = (dosha) => {
    const colors = {
      'vata': '#8b5cf6',
      'pitta': '#ef4444',
      'kapha': '#10b981'
    };
    return colors[dosha?.toLowerCase()] || '#64748b';
  };

  const getImbalanceColor = (level) => {
    const colors = {
      'mild': '#10b981',
      'moderate': '#f59e0b',
      'severe': '#ef4444'
    };
    return colors[level?.toLowerCase()] || '#64748b';
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading consultation history...</p>
      </div>
    );
  }

  return (
    <div className="history-container">
      <div className="history-header">
        <h1>Consultation History</h1>
        <p>View and download your past assessments</p>
      </div>

      {consultations.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📋</div>
          <h2>No Consultations Yet</h2>
          <p>Start your first assessment to see your consultation history here.</p>
          <button
            onClick={() => navigate('/assessment')}
            className="btn-primary"
          >
            Start Assessment
          </button>
        </div>
      ) : (
        <div className="consultations-grid">
          {consultations.map((consultation) => (
            <div key={consultation.id} className="consultation-card">
              <div className="consultation-header">
                <div className="consultation-date">
                  <span className="date-icon">📅</span>
                  <span>{new Date(consultation.timestamp).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}</span>
                </div>
                <div className="consultation-time">
                  {new Date(consultation.timestamp).toLocaleTimeString('en-US', {
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </div>
              </div>

              <div className="consultation-body">
                <div className="dosha-result">
                  <div className="result-label">Primary Dosha</div>
                  <div 
                    className="result-value dosha-badge"
                    style={{ backgroundColor: getDoshaColor(consultation.data.primary_dosha) }}
                  >
                    {consultation.data.primary_dosha?.toUpperCase() || 'N/A'}
                  </div>
                </div>

                <div className="imbalance-result">
                  <div className="result-label">Imbalance Level</div>
                  <div 
                    className="result-value imbalance-badge"
                    style={{ backgroundColor: getImbalanceColor(consultation.data.imbalance_level) }}
                  >
                    {consultation.data.imbalance_level || 'N/A'}
                  </div>
                </div>

                {consultation.data.dosha_scores && (
                  <div className="dosha-scores">
                    <div className="score-item">
                      <span>Vata:</span>
                      <span>{((consultation.data.dosha_scores.Vata || consultation.data.dosha_scores.vata || 0) * 100).toFixed(1)}%</span>
                    </div>
                    <div className="score-item">
                      <span>Pitta:</span>
                      <span>{((consultation.data.dosha_scores.Pitta || consultation.data.dosha_scores.pitta || 0) * 100).toFixed(1)}%</span>
                    </div>
                    <div className="score-item">
                      <span>Kapha:</span>
                      <span>{((consultation.data.dosha_scores.Kapha || consultation.data.dosha_scores.kapha || 0) * 100).toFixed(1)}%</span>
                    </div>
                  </div>
                )}
              </div>

              <div className="consultation-actions">
                <button
                  onClick={() => handleViewResults(consultation)}
                  className="btn-view"
                >
                  <svg width="16" height="16" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                    <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
                  </svg>
                  View Results
                </button>
                <button
                  onClick={() => handleDownloadPDF(consultation)}
                  className="btn-download"
                  disabled={downloadingId === consultation.id}
                >
                  {downloadingId === consultation.id ? (
                    <>
                      <svg className="spinner" width="16" height="16" viewBox="0 0 24 24" fill="none">
                        <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" opacity="0.25"/>
                        <path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" strokeWidth="4" strokeLinecap="round"/>
                      </svg>
                      Generating...
                    </>
                  ) : (
                    <>
                      <svg width="16" height="16" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
                      </svg>
                      Download PDF
                    </>
                  )}
                </button>
                <button
                  onClick={() => handleDeleteConsultation(consultation.id)}
                  className="btn-delete-small"
                >
                  <svg width="16" height="16" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ConsultationHistory;
