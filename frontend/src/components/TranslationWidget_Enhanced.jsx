import { useState } from 'react';
import voiceAssistantService from '../services/voiceAssistantService';
import '../styles/animations.css';

const TranslationWidget = () => {
  const [text, setText] = useState('');
  const [sourceLang, setSourceLang] = useState('auto');
  const [targetLang, setTargetLang] = useState('hi');
  const [translatedText, setTranslatedText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);
  
  const languages = [
    { code: 'auto', name: 'Auto-detect' },
    { code: 'en', name: 'English' },
    { code: 'hi', name: 'हिंदी (Hindi)' },
    { code: 'ta', name: 'தமிழ் (Tamil)' },
    { code: 'te', name: 'తెలుగు (Telugu)' },
    { code: 'bn', name: 'বাংলা (Bengali)' },
    { code: 'mr', name: 'मराठी (Marathi)' },
    { code: 'gu', name: 'ગુજરાતી (Gujarati)' },
    { code: 'kn', name: 'ಕನ್ನಡ (Kannada)' },
    { code: 'ml', name: 'മലയാളം (Malayalam)' },
    { code: 'pa', name: 'ਪੰਜਾਬੀ (Punjabi)' },
    { code: 'or', name: 'ଓଡ଼ିଆ (Odia)' }
  ];
  
  const handleTranslate = async () => {
    if (!text.trim()) {
      setError('Please enter text to translate');
      return;
    }
    
    setLoading(true);
    setError(null);
    setTranslatedText('');
    
    try {
      const result = await voiceAssistantService.translate(
        text,
        targetLang,
        sourceLang === 'auto' ? null : sourceLang
      );
      
      if (result.success) {
        setTranslatedText(result.translated_text);
      } else {
        setError(result.error || 'Translation failed');
      }
    } catch (err) {
      console.error('Translation error:', err);
      setError('Failed to translate. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  const handleSwapLanguages = () => {
    if (sourceLang !== 'auto') {
      const temp = sourceLang;
      setSourceLang(targetLang);
      setTargetLang(temp);
      setText(translatedText);
      setTranslatedText(text);
    }
  };
  
  const handleClear = () => {
    setText('');
    setTranslatedText('');
    setError(null);
    setCopied(false);
  };
  
  const handleCopy = () => {
    navigator.clipboard.writeText(translatedText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  
  return (
    <div style={styles.container} className="fade-in">
      <div style={styles.header}>
        <h3 style={styles.title}>🌐 Translation Tool</h3>
        <p style={styles.subtitle}>Translate text between languages</p>
      </div>
      
      <div style={styles.languageSelector} className="slide-in-down">
        <select 
          value={sourceLang} 
          onChange={(e) => setSourceLang(e.target.value)}
          style={styles.select}
          disabled={loading}
        >
          {languages.map(lang => (
            <option key={lang.code} value={lang.code}>
              {lang.name}
            </option>
          ))}
        </select>
        
        <button 
          onClick={handleSwapLanguages}
          style={styles.swapButton}
          className="button-hover ripple"
          disabled={loading || sourceLang === 'auto'}
          title="Swap languages"
        >
          ⇄
        </button>
        
        <select 
          value={targetLang} 
          onChange={(e) => setTargetLang(e.target.value)}
          style={styles.select}
          disabled={loading}
        >
          {languages.filter(l => l.code !== 'auto').map(lang => (
            <option key={lang.code} value={lang.code}>
              {lang.name}
            </option>
          ))}
        </select>
      </div>
      
      <div style={styles.textAreas} className="slide-in-up">
        <div style={styles.textAreaContainer}>
          <label style={styles.label}>Source Text</label>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Enter text to translate..."
            style={styles.textarea}
            rows={6}
            disabled={loading}
          />
          <div style={styles.charCount}>
            {text.length} characters
          </div>
        </div>
        
        <div style={styles.textAreaContainer}>
          <label style={styles.label}>Translation</label>
          <textarea
            value={translatedText}
            readOnly
            placeholder="Translation will appear here..."
            style={{...styles.textarea, backgroundColor: '#f5f5f5'}}
            rows={6}
            className={translatedText ? 'fade-in' : ''}
          />
          {translatedText && (
            <button
              onClick={handleCopy}
              style={styles.copyButton}
              className="button-hover ripple fade-in"
              title="Copy to clipboard"
            >
              {copied ? '✓ Copied!' : '📋 Copy'}
            </button>
          )}
        </div>
      </div>
      
      {error && (
        <div style={styles.error} className="fade-in error-shake">
          <span>⚠️</span>
          <span>{error}</span>
        </div>
      )}
      
      {loading && (
        <div className="loading-container fade-in" style={{padding: '20px'}}>
          <div className="spinner"></div>
          <p className="loading-text">Translating...</p>
        </div>
      )}
      
      <div style={styles.actions}>
        <button 
          onClick={handleTranslate} 
          disabled={loading || !text.trim()}
          style={{
            ...styles.button,
            ...styles.primaryButton,
            ...(loading || !text.trim() ? styles.disabledButton : {})
          }}
          className={loading || !text.trim() ? '' : 'button-hover ripple'}
        >
          {loading ? (
            <span style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
              <div className="spinner spinner-small" style={{borderTopColor: 'white'}}></div>
              <span>Translating</span>
            </span>
          ) : (
            '🔄 Translate'
          )}
        </button>
        
        <button 
          onClick={handleClear}
          disabled={loading || (!text && !translatedText)}
          style={{
            ...styles.button,
            ...styles.secondaryButton,
            ...(loading || (!text && !translatedText) ? styles.disabledButton : {})
          }}
          className={loading || (!text && !translatedText) ? '' : 'button-hover'}
        >
          🗑️ Clear
        </button>
      </div>
    </div>
  );
};

const styles = {
  container: {
    maxWidth: '900px',
    margin: '0 auto',
    padding: '24px',
    backgroundColor: 'white',
    borderRadius: '12px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
  },
  header: {
    textAlign: 'center',
    marginBottom: '24px'
  },
  title: {
    margin: '0 0 8px 0',
    fontSize: '24px',
    color: '#333'
  },
  subtitle: {
    margin: 0,
    fontSize: '14px',
    color: '#666'
  },
  languageSelector: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    marginBottom: '20px',
    justifyContent: 'center'
  },
  select: {
    flex: 1,
    maxWidth: '250px',
    padding: '10px',
    fontSize: '14px',
    border: '1px solid #ddd',
    borderRadius: '6px',
    backgroundColor: 'white',
    cursor: 'pointer'
  },
  swapButton: {
    padding: '10px 16px',
    fontSize: '20px',
    border: '1px solid #ddd',
    borderRadius: '6px',
    backgroundColor: 'white',
    cursor: 'pointer',
    transition: 'all 0.2s'
  },
  textAreas: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '20px',
    marginBottom: '20px'
  },
  textAreaContainer: {
    position: 'relative'
  },
  label: {
    display: 'block',
    marginBottom: '8px',
    fontSize: '14px',
    fontWeight: '500',
    color: '#555'
  },
  textarea: {
    width: '100%',
    padding: '12px',
    fontSize: '14px',
    border: '1px solid #ddd',
    borderRadius: '6px',
    resize: 'vertical',
    fontFamily: 'inherit',
    lineHeight: '1.5'
  },
  charCount: {
    position: 'absolute',
    bottom: '8px',
    right: '12px',
    fontSize: '12px',
    color: '#999'
  },
  copyButton: {
    position: 'absolute',
    top: '32px',
    right: '8px',
    padding: '6px 12px',
    fontSize: '12px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    backgroundColor: 'white',
    cursor: 'pointer',
    transition: 'all 0.2s'
  },
  error: {
    padding: '12px',
    backgroundColor: '#ffebee',
    color: '#c62828',
    borderRadius: '6px',
    marginBottom: '16px',
    display: 'flex',
    alignItems: 'center',
    gap: '8px'
  },
  actions: {
    display: 'flex',
    gap: '12px',
    justifyContent: 'center'
  },
  button: {
    padding: '12px 32px',
    fontSize: '16px',
    fontWeight: '500',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'all 0.3s',
    display: 'flex',
    alignItems: 'center',
    gap: '8px'
  },
  primaryButton: {
    backgroundColor: '#4CAF50',
    color: 'white'
  },
  secondaryButton: {
    backgroundColor: '#f5f5f5',
    color: '#333',
    border: '1px solid #ddd'
  },
  disabledButton: {
    opacity: 0.5,
    cursor: 'not-allowed'
  }
};

export default TranslationWidget;
