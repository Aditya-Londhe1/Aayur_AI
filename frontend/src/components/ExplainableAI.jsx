import React, { useState } from 'react'

function ExplainableAI({ analysis, language }) {
  const [expandedSection, setExpandedSection] = useState(null)

  if (!analysis) {
    return null
  }

  const toggleSection = (section) => {
    setExpandedSection(expandedSection === section ? null : section)
  }

  const renderConfidenceBar = (confidence) => {
    const percentage = Math.round(confidence * 100)
    let color = '#4CAF50' // Green
    if (percentage < 50) color = '#f44336' // Red
    else if (percentage < 75) color = '#ff9800' // Orange
    
    return (
      <div className="confidence-bar-container">
        <div className="confidence-bar">
          <div
            className="confidence-fill"
            style={{ width: `${percentage}%`, backgroundColor: color }}
          >
            {percentage}%
          </div>
        </div>
        <span className="confidence-label">
          {percentage >= 75 ? 'High Confidence' : percentage >= 50 ? 'Moderate Confidence' : 'Low Confidence'}
        </span>
      </div>
    )
  }

  const renderDoshaScores = (scores) => {
    if (!scores) return null
    
    const doshas = ['vata', 'pitta', 'kapha']
    const maxScore = Math.max(...doshas.map(d => scores[d] || 0))
    
    return (
      <div className="dosha-scores">
        {doshas.map(dosha => {
          const score = scores[dosha] || 0
          const percentage = maxScore > 0 ? (score / maxScore) * 100 : 0
          const isHighest = score === maxScore
          
          return (
            <div key={dosha} className={`dosha-score-item ${isHighest ? 'highest' : ''}`}>
              <div className="dosha-name">
                <span className="dosha-icon">
                  {dosha === 'vata' ? '💨' : dosha === 'pitta' ? '🔥' : '🌊'}
                </span>
                <span>{dosha.charAt(0).toUpperCase() + dosha.slice(1)}</span>
                {isHighest && <span className="badge">Dominant</span>}
              </div>
              <div className="dosha-bar">
                <div
                  className="dosha-fill"
                  style={{
                    width: `${percentage}%`,
                    backgroundColor: dosha === 'vata' ? '#9C27B0' : dosha === 'pitta' ? '#FF5722' : '#2196F3'
                  }}
                />
              </div>
              <span className="dosha-value">{score.toFixed(2)}</span>
            </div>
          )
        })}
      </div>
    )
  }

  const renderModalityExplanation = (modality, data) => {
    if (!data) return null
    
    const icons = {
      tongue: '👅',
      pulse: '💓',
      symptoms: '📝',
      voice: '🎤'
    }
    
    return (
      <div className="modality-explanation">
        <div
          className="modality-header"
          onClick={() => toggleSection(modality)}
        >
          <span className="modality-icon">{icons[modality] || '🔍'}</span>
          <h3>{modality.charAt(0).toUpperCase() + modality.slice(1)} Analysis</h3>
          <span className="expand-icon">{expandedSection === modality ? '▼' : '▶'}</span>
        </div>
        
        {expandedSection === modality && (
          <div className="modality-content">
            {data.confidence !== undefined && (
              <div className="modality-confidence">
                <strong>AI Confidence:</strong>
                {renderConfidenceBar(data.confidence)}
              </div>
            )}
            
            {data.contribution && (
              <div className="modality-contribution">
                <strong>Contribution:</strong>
                <p>{data.contribution}</p>
              </div>
            )}
            
            {data.details && (
              <div className="modality-details">
                <strong>Details:</strong>
                <p>{data.details}</p>
              </div>
            )}
            
            {data.key_features && (
              <div className="modality-features">
                <strong>Key Features Detected:</strong>
                <ul>
                  {Object.entries(data.key_features).map(([key, value]) => (
                    <li key={key}>
                      <span className="feature-name">{key.replace(/_/g, ' ')}:</span>
                      <span className="feature-value">{typeof value === 'number' ? value.toFixed(2) : value}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {data.supporting_symptoms && data.supporting_symptoms.length > 0 && (
              <div className="supporting-symptoms">
                <strong>Supporting Symptoms:</strong>
                <div className="symptom-chips">
                  {data.supporting_symptoms.map((symptom, idx) => (
                    <span key={idx} className="chip">{symptom}</span>
                  ))}
                </div>
              </div>
            )}
            
            {data.heatmap && (
              <div className="heatmap-visualization">
                <strong>Visual Explanation (Grad-CAM):</strong>
                <img
                  src={`data:image/png;base64,${data.heatmap}`}
                  alt="AI attention heatmap"
                  className="heatmap-image"
                />
                <p className="heatmap-caption">
                  Red areas show where the AI focused its attention during analysis
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="explainable-ai-section">
      <div className="xai-header">
        <h2>🧠 AI Explanation & Transparency</h2>
        <p className="xai-subtitle">
          Understanding how AI reached this diagnosis
        </p>
      </div>

      {/* Overall Confidence */}
      {analysis.confidence !== undefined && (
        <div className="overall-confidence card">
          <h3>Overall AI Confidence</h3>
          {renderConfidenceBar(analysis.confidence)}
          <p className="confidence-note">
            This score represents how certain the AI is about the diagnosis based on the provided data.
          </p>
        </div>
      )}

      {/* Dosha Scores */}
      {analysis.dosha_scores && (
        <div className="dosha-analysis card">
          <h3>Dosha Distribution</h3>
          {renderDoshaScores(analysis.dosha_scores)}
          <p className="dosha-note">
            The AI calculated these scores by analyzing multiple physiological markers and symptoms.
          </p>
        </div>
      )}

      {/* Modality Explanations */}
      {analysis.explainability && (
        <div className="modalities-section card">
          <h3>Analysis by Modality</h3>
          <p className="modalities-intro">
            Each diagnostic method contributed to the final result. Click to expand details:
          </p>
          
          {analysis.explainability.modalities && Object.entries(analysis.explainability.modalities).map(([modality, data]) => (
            <div key={modality}>
              {renderModalityExplanation(modality, data)}
            </div>
          ))}
        </div>
      )}

      {/* Summary Explanation */}
      {analysis.explainability?.summary && (
        <div className="summary-explanation card">
          <h3>Summary</h3>
          <p>{analysis.explainability.summary}</p>
        </div>
      )}

      {/* AI Model Information */}
      <div className="ai-model-info card">
        <h3>🤖 AI Technologies Used</h3>
        <div className="tech-grid">
          <div className="tech-item">
            <span className="tech-icon">🧠</span>
            <div>
              <strong>Deep Learning</strong>
              <p>Neural networks trained on extensive datasets</p>
            </div>
          </div>
          <div className="tech-item">
            <span className="tech-icon">👁️</span>
            <div>
              <strong>Computer Vision</strong>
              <p>CNN-based image analysis with Grad-CAM explainability</p>
            </div>
          </div>
          <div className="tech-item">
            <span className="tech-icon">📊</span>
            <div>
              <strong>Signal Processing</strong>
              <p>FFT and time-domain analysis for pulse data</p>
            </div>
          </div>
          <div className="tech-item">
            <span className="tech-icon">💬</span>
            <div>
              <strong>NLP</strong>
              <p>Natural language understanding for symptoms</p>
            </div>
          </div>
        </div>
      </div>

      {/* Disclaimer */}
      <div className="xai-disclaimer">
        <p>
          <strong>⚠️ Important:</strong> This AI system provides educational insights and preventive wellness guidance.
          It does not diagnose medical conditions. Always consult qualified healthcare practitioners for medical advice.
        </p>
      </div>
    </div>
  )
}

export default ExplainableAI
