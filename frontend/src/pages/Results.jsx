import { useState, useEffect } from 'react'
import { useLocation, useNavigate, Link } from 'react-router-dom'
import ExplainableAI from '../components/ExplainableAI'

function Results({ language }) {
  const location = useLocation()
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState('home_remedies')

  const { result, patientInfo, fromHistory } = location.state || {}

  // Save consultation to history (only if not viewing from history)
  useEffect(() => {
    if (result && !fromHistory) {
      saveToHistory(result);
    }
  }, [result, fromHistory]);

  const saveToHistory = (diagnosisResult) => {
    try {
      // Extract the actual diagnosis data
      const diagnosis = diagnosisResult.diagnosis || diagnosisResult;
      
      // Prepare complete consultation data for storage and PDF generation
      const consultation = {
        id: Date.now(),
        timestamp: new Date().toISOString(),
        data: {
          // Core diagnosis data
          primary_dosha: diagnosis.dominant_dosha,
          dominant_dosha: diagnosis.dominant_dosha,
          imbalance_level: diagnosis.imbalance_level,
          dosha_scores: diagnosis.dosha_scores,
          confidence: diagnosisResult.confidence || 0,
          
          // Analysis details
          pulse_analysis: diagnosisResult.analyses?.pulse,
          tongue_analysis: diagnosisResult.analyses?.tongue,
          symptom_analysis: diagnosisResult.analyses?.symptoms,
          
          // Fusion details
          fusion_details: diagnosis.fusion_details,
          
          // Recommendations
          recommendations: diagnosisResult.recommendations,
          home_remedies: diagnosisResult.recommendations?.ayurvedic_home_remedies,
          
          // Patient info
          patient_info: {
            name: patientInfo?.name,
            age: patientInfo?.age,
            gender: patientInfo?.gender
          },
          
          // Additional diagnosis info
          prakriti_type: diagnosis.prakriti_type,
          vikriti_type: diagnosis.vikriti_type,
          explanation: diagnosis.explanation,
          likely_conditions: diagnosis.likely_conditions
        },
        patientInfo: patientInfo
      };

      // Get existing history
      const stored = localStorage.getItem('consultation_history');
      const history = stored ? JSON.parse(stored) : [];

      // Check if this consultation already exists (within last 5 seconds to prevent duplicates)
      const now = Date.now();
      const isDuplicate = history.some(item => {
        const timeDiff = now - item.id;
        return timeDiff < 5000 && // Within 5 seconds
               item.data.primary_dosha === consultation.data.primary_dosha &&
               item.data.confidence === consultation.data.confidence;
      });

      if (isDuplicate) {
        console.log('⚠️ Duplicate consultation detected, skipping save');
        return;
      }

      // Add new consultation
      history.unshift(consultation);

      // Keep only last 50 consultations
      const trimmed = history.slice(0, 50);

      // Save back to localStorage
      localStorage.setItem('consultation_history', JSON.stringify(trimmed));
      
      console.log('✅ Consultation saved to history:', consultation);
    } catch (error) {
      console.error('Failed to save consultation to history:', error);
    }
  };

  // Redirect if no data
  if (!result) {
    return (
      <div className="results-container">
        <div className="card text-center">
          <h2>No Results Available</h2>
          <p>Please complete an assessment first.</p>
          <Link to="/assessment" className="btn btn-primary mt-3">
            <span className="ai-icon">🤖</span> Start AI Assessment
          </Link>
        </div>
      </div>
    )
  }

  const diagnosis = result.diagnosis || {}
  const recommendations = result.recommendations || {}
  const confidence = result.confidence || 0

  const doshaScores = diagnosis.dosha_scores || { vata: 0.33, pitta: 0.33, kapha: 0.33 }
  const dominantDosha = diagnosis.dominant_dosha || 'balanced'
  const imbalanceLevel = diagnosis.imbalance_level || 'mild'

  // Dosha information
  const doshaInfo = {
    vata: {
      icon: '💨',
      name: 'Vata',
      element: 'Air + Space',
      qualities: 'Light, Dry, Cold, Mobile',
      color: '#9c27b0'
    },
    pitta: {
      icon: '🔥',
      name: 'Pitta',
      element: 'Fire + Water',
      qualities: 'Hot, Sharp, Light, Oily',
      color: '#ff5722'
    },
    kapha: {
      icon: '🌊',
      name: 'Kapha',
      element: 'Earth + Water',
      qualities: 'Heavy, Slow, Cool, Oily',
      color: '#4caf50'
    }
  }

  const getConfidenceColor = (conf) => {
    if (conf >= 0.8) return 'var(--success)'
    if (conf >= 0.6) return 'var(--warning)'
    return 'var(--error)'
  }

  const getImbalanceColor = (level) => {
    if (level === 'severe') return 'var(--error)'
    if (level === 'moderate') return 'var(--warning)'
    return 'var(--success)'
  }

  return (
    <div className="results-container fade-in">
      {/* AI Analysis Banner */}
      <div className="ai-results-banner">
        <div className="ai-badge-large">
          <span className="ai-icon">🤖</span>
          <span>AI-Powered Analysis Complete</span>
        </div>
        <p>Your results have been generated using advanced AI algorithms</p>
      </div>

      {/* Header */}
      <div className="card">
        <div className="card-header">
          <h1>Your Ayurvedic Analysis Results</h1>
          <div className="ai-indicator-small">🤖 Generated by Multi-Modal AI Fusion</div>
        </div>
        <div className="card-body">
          <div className="flex-between">
            <div>
              <p><strong>Patient:</strong> {patientInfo?.name || 'N/A'}</p>
              <p><strong>Age:</strong> {patientInfo?.age || 'N/A'} years</p>
              <p><strong>Gender:</strong> {patientInfo?.gender || 'N/A'}</p>
            </div>
            <div className="text-right">
              <p><strong>Analysis Date:</strong> {new Date().toLocaleDateString()}</p>
              <p>
                <strong>🤖 AI Confidence Score:</strong>{' '}
                <span style={{ color: getConfidenceColor(confidence), fontWeight: 700 }}>
                  {(confidence * 100).toFixed(1)}%
                </span>
              </p>
              <div className="confidence-bar-small">
                <div 
                  className="confidence-fill-small" 
                  style={{ 
                    width: `${confidence * 100}%`,
                    background: getConfidenceColor(confidence)
                  }}
                />
              </div>
              <small className="text-secondary">
                {confidence >= 0.8 ? '✓ High AI confidence' : 
                 confidence >= 0.6 ? '⚠ Moderate AI confidence' : 
                 '⚠ Low AI confidence - consult expert'}
              </small>
            </div>
          </div>
        </div>
      </div>

      {/* Dosha Scores */}
      <div className="card">
        <div className="card-header">
          <h2>Your Dosha Balance</h2>
        </div>
        <div className="card-body">
          {/* Analyses Performed */}
          {result.analyses && (
            <div style={{
              background: 'var(--primary-lighter)',
              padding: '1rem',
              borderRadius: '12px',
              marginBottom: '2rem',
              display: 'flex',
              gap: '1rem',
              flexWrap: 'wrap',
              justifyContent: 'center'
            }}>
              <strong style={{ width: '100%', textAlign: 'center', marginBottom: '0.5rem' }}>
                🤖 AI Analyses Performed:
              </strong>
              {result.analyses.pulse && (
                <div style={{
                  background: 'white',
                  padding: '0.5rem 1rem',
                  borderRadius: '20px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  border: '2px solid var(--accent)'
                }}>
                  <span>💓</span>
                  <span style={{ fontWeight: 600 }}>Pulse Analysis (Nadi Pariksha)</span>
                  <span style={{ 
                    background: 'var(--success)', 
                    color: 'white', 
                    padding: '0.125rem 0.5rem', 
                    borderRadius: '10px',
                    fontSize: '0.75rem',
                    fontWeight: 700
                  }}>✓</span>
                </div>
              )}
              {result.analyses.symptoms && (
                <div style={{
                  background: 'white',
                  padding: '0.5rem 1rem',
                  borderRadius: '20px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  border: '2px solid var(--accent)'
                }}>
                  <span>📝</span>
                  <span style={{ fontWeight: 600 }}>Symptom Analysis</span>
                  <span style={{ 
                    background: 'var(--success)', 
                    color: 'white', 
                    padding: '0.125rem 0.5rem', 
                    borderRadius: '10px',
                    fontSize: '0.75rem',
                    fontWeight: 700
                  }}>✓</span>
                </div>
              )}
              {result.analyses.tongue && (
                <div style={{
                  background: 'white',
                  padding: '0.5rem 1rem',
                  borderRadius: '20px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  border: '2px solid var(--accent)'
                }}>
                  <span>👅</span>
                  <span style={{ fontWeight: 600 }}>Tongue Analysis</span>
                  <span style={{ 
                    background: 'var(--success)', 
                    color: 'white', 
                    padding: '0.125rem 0.5rem', 
                    borderRadius: '10px',
                    fontSize: '0.75rem',
                    fontWeight: 700
                  }}>✓</span>
                </div>
              )}
            </div>
          )}
          
          {/* Ayurvedic Pulse Interpretation */}
          {result.analyses?.pulse?.ayurvedic_analysis && (
            <div style={{
              background: 'linear-gradient(135deg, rgba(255, 215, 0, 0.1) 0%, rgba(255, 140, 0, 0.1) 100%)',
              padding: '1.5rem',
              borderRadius: '16px',
              border: '2px solid rgba(255, 165, 0, 0.3)',
              marginBottom: '1.5rem'
            }}>
              <h3 style={{ 
                color: 'var(--primary)', 
                marginBottom: '1rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem'
              }}>
                🕉️ Traditional Ayurvedic Pulse Analysis (Nadi Pariksha)
              </h3>
              
              {result.analyses.pulse.ayurvedic_analysis.interpretation && (
                <div style={{
                  background: 'white',
                  padding: '1rem',
                  borderRadius: '12px',
                  marginBottom: '1rem',
                  fontStyle: 'italic',
                  lineHeight: '1.6'
                }}>
                  {result.analyses.pulse.ayurvedic_analysis.interpretation}
                </div>
              )}
              
              {result.analyses.pulse.ayurvedic_analysis.ayurvedic_insights && 
               result.analyses.pulse.ayurvedic_analysis.ayurvedic_insights.length > 0 && (
                <div style={{ marginTop: '1rem' }}>
                  <strong>📿 Ayurvedic Insights:</strong>
                  <ul style={{ marginTop: '0.5rem', paddingLeft: '1.5rem' }}>
                    {result.analyses.pulse.ayurvedic_analysis.ayurvedic_insights.map((insight, idx) => (
                      <li key={idx} style={{ marginBottom: '0.25rem' }}>{insight}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {result.analyses.pulse.ayurvedic_analysis.traditional_characteristics && (
                <div style={{ 
                  marginTop: '1rem',
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                  gap: '0.75rem'
                }}>
                  <div style={{ background: 'white', padding: '0.75rem', borderRadius: '8px' }}>
                    <strong>Gati (Movement):</strong> {result.analyses.pulse.ayurvedic_analysis.traditional_characteristics.gati}
                  </div>
                  <div style={{ background: 'white', padding: '0.75rem', borderRadius: '8px' }}>
                    <strong>Speed:</strong> {result.analyses.pulse.ayurvedic_analysis.traditional_characteristics.speed}
                  </div>
                  <div style={{ background: 'white', padding: '0.75rem', borderRadius: '8px' }}>
                    <strong>Force:</strong> {result.analyses.pulse.ayurvedic_analysis.traditional_characteristics.force}
                  </div>
                  <div style={{ background: 'white', padding: '0.75rem', borderRadius: '8px' }}>
                    <strong>Rhythm:</strong> {result.analyses.pulse.ayurvedic_analysis.traditional_characteristics.rhythm}
                  </div>
                </div>
              )}
            </div>
          )}
          
          <div className="dosha-scores">
            {Object.entries(doshaScores).map(([dosha, score]) => (
              <div
                key={dosha}
                className={`dosha-card ${dominantDosha === dosha ? 'dominant' : ''}`}
              >
                <div className="dosha-icon">{doshaInfo[dosha].icon}</div>
                <div className="dosha-name">{doshaInfo[dosha].name}</div>
                <div className="dosha-score">{(score * 100).toFixed(0)}%</div>
                <div className="dosha-label">{doshaInfo[dosha].element}</div>
                {dominantDosha === dosha && (
                  <div className="mt-2">
                    <span style={{
                      background: 'var(--primary)',
                      color: 'white',
                      padding: '0.25rem 0.75rem',
                      borderRadius: '12px',
                      fontSize: '0.875rem',
                      fontWeight: 600
                    }}>
                      Dominant
                    </span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Diagnosis Summary */}
      <div className="card">
        <div className="card-header">
          <h2>Diagnosis Summary</h2>
        </div>
        <div className="card-body">
          <div className="grid grid-2">
            <div>
              <h3 className="text-primary mb-2">Dominant Dosha</h3>
              <p className="mb-3">
                <strong style={{ fontSize: '1.5rem' }}>
                  {doshaInfo[dominantDosha]?.name || 'Balanced'}
                </strong>
              </p>
              <p>{diagnosis.explanation || 'Your doshas are in balance.'}</p>
            </div>
            <div>
              <h3 className="text-primary mb-2">Imbalance Level</h3>
              <p className="mb-3">
                <strong
                  style={{
                    fontSize: '1.5rem',
                    color: getImbalanceColor(imbalanceLevel)
                  }}
                >
                  {imbalanceLevel.charAt(0).toUpperCase() + imbalanceLevel.slice(1)}
                </strong>
              </p>
              <p>
                <strong>Prakriti (Constitution):</strong> {diagnosis.prakriti_type || 'Unknown'}
              </p>
              <p>
                <strong>Vikriti (Current State):</strong> {diagnosis.vikriti_type || 'Unknown'}
              </p>
            </div>
          </div>

          {/* Fusion Details */}
          {diagnosis.fusion_details && (
            <div className="mt-4" style={{
              background: 'linear-gradient(135deg, rgba(14, 165, 233, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%)',
              padding: '1.5rem',
              borderRadius: '16px',
              border: '2px solid var(--primary-lighter)'
            }}>
              <h3 className="text-primary mb-3">
                🔬 Multi-Modal Fusion Analysis
              </h3>
              
              {/* Modality Weights */}
              {diagnosis.fusion_details.weights_used && (
                <div className="mb-3">
                  <h4 style={{ fontSize: '1rem', marginBottom: '0.75rem' }}>Analysis Weights:</h4>
                  <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                    {Object.entries(diagnosis.fusion_details.weights_used).map(([modality, weight]) => (
                      <div key={modality} style={{
                        background: 'white',
                        padding: '0.5rem 1rem',
                        borderRadius: '12px',
                        border: '2px solid var(--primary)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem'
                      }}>
                        <span style={{ fontSize: '1.25rem' }}>
                          {modality === 'pulse' ? '💓' : modality === 'tongue' ? '👅' : '📝'}
                        </span>
                        <span style={{ fontWeight: 600 }}>
                          {modality.charAt(0).toUpperCase() + modality.slice(1)}:
                        </span>
                        <span style={{ color: 'var(--primary)', fontWeight: 700 }}>
                          {(weight * 100).toFixed(0)}%
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Source Contributions */}
              {diagnosis.fusion_details.sources && (
                <div>
                  <h4 style={{ fontSize: '1rem', marginBottom: '0.75rem' }}>
                    Individual Modality Predictions:
                  </h4>
                  {Object.entries(diagnosis.fusion_details.sources).map(([modality, scores]) => {
                    // Skip if all scores are 0
                    const hasData = Object.values(scores).some(v => v > 0)
                    if (!hasData) return null
                    
                    return (
                      <div key={modality} style={{
                        background: 'white',
                        padding: '1rem',
                        borderRadius: '12px',
                        marginBottom: '0.75rem',
                        border: '1px solid var(--border)'
                      }}>
                        <div style={{ 
                          display: 'flex', 
                          alignItems: 'center', 
                          gap: '0.5rem',
                          marginBottom: '0.75rem'
                        }}>
                          <span style={{ fontSize: '1.5rem' }}>
                            {modality === 'pulse' ? '💓' : modality === 'tongue' ? '👅' : '📝'}
                          </span>
                          <strong>{modality.charAt(0).toUpperCase() + modality.slice(1)} Analysis</strong>
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                          {Object.entries(scores).map(([dosha, score]) => (
                            <div key={dosha} style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                              <span style={{ minWidth: '60px', fontWeight: 600 }}>
                                {dosha.charAt(0).toUpperCase() + dosha.slice(1)}:
                              </span>
                              <div style={{
                                flex: 1,
                                height: '24px',
                                background: 'var(--gray-200)',
                                borderRadius: '12px',
                                overflow: 'hidden'
                              }}>
                                <div style={{
                                  width: `${score * 100}%`,
                                  height: '100%',
                                  background: dosha.toLowerCase() === 'vata' ? '#9C27B0' : 
                                             dosha.toLowerCase() === 'pitta' ? '#FF5722' : '#2196F3',
                                  transition: 'width 0.5s ease'
                                }} />
                              </div>
                              <span style={{ minWidth: '50px', textAlign: 'right', fontWeight: 700 }}>
                                {(score * 100).toFixed(1)}%
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}

              <p style={{ 
                marginTop: '1rem', 
                fontSize: '0.9rem', 
                color: 'var(--text-secondary)',
                fontStyle: 'italic'
              }}>
                ℹ️ The final diagnosis is calculated by combining predictions from all modalities 
                using weighted averaging based on their reliability and contribution.
              </p>
            </div>
          )}

          {diagnosis.likely_conditions && diagnosis.likely_conditions.length > 0 && (
            <div className="mt-4">
              <h3 className="text-primary mb-2">Likely Conditions</h3>
              <ul style={{ paddingLeft: '1.5rem' }}>
                {diagnosis.likely_conditions.map((condition, index) => (
                  <li key={index}>
                    <strong>{condition.name}</strong>
                    {condition.confidence && ` (${(condition.confidence * 100).toFixed(0)}% confidence)`}
                    {condition.description && ` - ${condition.description}`}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      {/* Recommendations */}
      <div className="card recommendations">
        <div className="card-header">
          <h2>🌿 Personalized Ayurvedic Recommendations</h2>
        </div>
        <div className="card-body">
          <div className="recommendation-tabs">
            <button
              className={`tab-button ${activeTab === 'home_remedies' ? 'active' : ''}`}
              onClick={() => setActiveTab('home_remedies')}
            >
              🏠 Home Remedies
            </button>
            <button
              className={`tab-button ${activeTab === 'dietary' ? 'active' : ''}`}
              onClick={() => setActiveTab('dietary')}
            >
              🍽️ Dietary
            </button>
            <button
              className={`tab-button ${activeTab === 'lifestyle' ? 'active' : ''}`}
              onClick={() => setActiveTab('lifestyle')}
            >
              🧘 Lifestyle
            </button>
            <button
              className={`tab-button ${activeTab === 'herbal' ? 'active' : ''}`}
              onClick={() => setActiveTab('herbal')}
            >
              🌿 Herbal
            </button>
            {recommendations.yoga && (
              <button
                className={`tab-button ${activeTab === 'yoga' ? 'active' : ''}`}
                onClick={() => setActiveTab('yoga')}
              >
                🧘‍♀️ Yoga
              </button>
            )}
          </div>

          <div className="tab-content">
            {/* Ayurvedic Home Remedies Tab */}
            {activeTab === 'home_remedies' && recommendations.ayurvedic_home_remedies && (
              <div className="ayurvedic-remedies-section">
                {recommendations.remedy_description && (
                  <div className="alert alert-info mb-3">
                    <strong>ℹ️ About {dominantDosha.charAt(0).toUpperCase() + dominantDosha.slice(1)} Imbalance:</strong>
                    <p style={{ marginTop: '0.5rem', marginBottom: 0 }}>{recommendations.remedy_description}</p>
                  </div>
                )}
                
                <div className="remedies-grid">
                  {recommendations.ayurvedic_home_remedies.map((remedy, index) => (
                    <div key={index} className="remedy-card">
                      <div className="remedy-header">
                        <h3>{remedy.name}</h3>
                        <span className="difficulty-badge" style={{
                          background: remedy.difficulty === 'Very Easy' ? 'var(--success)' : 
                                     remedy.difficulty === 'Easy' ? 'var(--info)' : 'var(--warning)',
                          color: 'white',
                          padding: '0.25rem 0.75rem',
                          borderRadius: '12px',
                          fontSize: '0.75rem',
                          fontWeight: 600
                        }}>
                          {remedy.difficulty}
                        </span>
                      </div>
                      
                      <div className="remedy-body">
                        <div className="remedy-section">
                          <strong>🥘 Ingredients:</strong>
                          <ul>
                            {remedy.ingredients.map((ing, i) => (
                              <li key={i}>{ing}</li>
                            ))}
                          </ul>
                        </div>
                        
                        <div className="remedy-section">
                          <strong>📝 Preparation:</strong>
                          <p>{remedy.preparation}</p>
                        </div>
                        
                        <div className="remedy-section">
                          <strong>💊 Usage:</strong>
                          <p>{remedy.usage}</p>
                        </div>
                        
                        <div className="remedy-section">
                          <strong>✨ Benefits:</strong>
                          <p>{remedy.benefits}</p>
                        </div>
                        
                        <div className="remedy-timing">
                          <span>⏰ Best Time: {remedy.time}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                
                {/* Ayurvedic Dietary Remedies */}
                {recommendations.ayurvedic_dietary && recommendations.ayurvedic_dietary.length > 0 && (
                  <div className="mt-4">
                    <h3 className="text-primary mb-2">🍲 Ayurvedic Dietary Remedies</h3>
                    <div className="remedies-grid">
                      {recommendations.ayurvedic_dietary.map((remedy, index) => (
                        <div key={index} className="remedy-card">
                          <h4>{remedy.name}</h4>
                          <div className="remedy-section">
                            <strong>Ingredients:</strong>
                            <ul>
                              {remedy.ingredients.map((ing, i) => (
                                <li key={i}>{ing}</li>
                              ))}
                            </ul>
                          </div>
                          <div className="remedy-section">
                            <strong>Preparation:</strong>
                            <p>{remedy.preparation}</p>
                          </div>
                          <div className="remedy-section">
                            <strong>Benefits:</strong>
                            <p>{remedy.benefits}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* Lifestyle Remedies */}
                {recommendations.ayurvedic_lifestyle && recommendations.ayurvedic_lifestyle.length > 0 && (
                  <div className="mt-4">
                    <h3 className="text-primary mb-2">🌅 Ayurvedic Lifestyle Practices</h3>
                    <ul className="recommendation-list">
                      {recommendations.ayurvedic_lifestyle.map((item, index) => (
                        <li key={index}>{item}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
            {activeTab === 'dietary' && recommendations.dietary && (
              <ul className="recommendation-list">
                {recommendations.dietary.map((item, index) => (
                  <li key={index}>{item}</li>
                ))}
              </ul>
            )}

            {activeTab === 'lifestyle' && recommendations.lifestyle && (
              <ul className="recommendation-list">
                {recommendations.lifestyle.map((item, index) => (
                  <li key={index}>{item}</li>
                ))}
              </ul>
            )}

            {activeTab === 'herbal' && recommendations.herbal && (
              <ul className="recommendation-list">
                {recommendations.herbal.map((item, index) => (
                  <li key={index}>{item}</li>
                ))}
              </ul>
            )}

            {activeTab === 'yoga' && recommendations.yoga && (
              <ul className="recommendation-list">
                {recommendations.yoga.map((item, index) => (
                  <li key={index}>{item}</li>
                ))}
              </ul>
            )}
          </div>

          {recommendations.precautions && recommendations.precautions.length > 0 && (
            <div className="alert alert-warning mt-4">
              <strong>⚠️ Precautions:</strong>
              <ul style={{ marginTop: '0.5rem', paddingLeft: '1.5rem' }}>
                {recommendations.precautions.map((precaution, index) => (
                  <li key={index}>{precaution}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      {/* Disclaimer */}
      <div className="alert alert-info">
        <strong>📋 Medical Disclaimer:</strong> {recommendations.disclaimer || 
          'This analysis is for educational purposes only and should not replace professional medical advice. Always consult qualified healthcare practitioners for diagnosis and treatment.'}
      </div>

      {/* Explainable AI Section */}
      <ExplainableAI analysis={result} language={language} />

      {/* Actions */}
      <div className="flex-center gap-3 mt-4">
        <button className="btn btn-secondary" onClick={() => navigate('/assessment')}>
          Take Another Assessment
        </button>
        <button className="btn btn-primary" onClick={() => window.print()}>
          Print Results
        </button>
      </div>
    </div>
  )
}

export default Results
