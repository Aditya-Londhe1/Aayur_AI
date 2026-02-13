import TranslationWidget from '../components/TranslationWidget';

const TranslationPage = () => {
  return (
    <div style={styles.container}>
      <div style={styles.content}>
        <TranslationWidget />
        
        <div style={styles.info}>
          <h4 style={styles.infoTitle}>About Translation</h4>
          <p style={styles.infoText}>
            Our translation tool supports 11 Indian languages and English. 
            It uses advanced AI to provide accurate translations while maintaining 
            the context and meaning of health-related terms.
          </p>
          
          <div style={styles.features}>
            <div style={styles.feature}>
              <span style={styles.featureIcon}>✓</span>
              <span>Auto language detection</span>
            </div>
            <div style={styles.feature}>
              <span style={styles.featureIcon}>✓</span>
              <span>Medical term accuracy</span>
            </div>
            <div style={styles.feature}>
              <span style={styles.featureIcon}>✓</span>
              <span>11 Indian languages</span>
            </div>
            <div style={styles.feature}>
              <span style={styles.featureIcon}>✓</span>
              <span>Instant translation</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const styles = {
  container: {
    minHeight: '100vh',
    backgroundColor: '#f5f5f5',
    padding: '40px 20px'
  },
  content: {
    maxWidth: '1000px',
    margin: '0 auto'
  },
  info: {
    marginTop: '32px',
    padding: '24px',
    backgroundColor: 'white',
    borderRadius: '12px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
  },
  infoTitle: {
    margin: '0 0 12px 0',
    fontSize: '20px',
    color: '#333'
  },
  infoText: {
    margin: '0 0 20px 0',
    fontSize: '15px',
    lineHeight: '1.6',
    color: '#666'
  },
  features: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '12px'
  },
  feature: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '12px',
    backgroundColor: '#f9f9f9',
    borderRadius: '8px',
    fontSize: '14px',
    color: '#555'
  },
  featureIcon: {
    color: '#4CAF50',
    fontWeight: 'bold',
    fontSize: '16px'
  }
};

export default TranslationPage;
