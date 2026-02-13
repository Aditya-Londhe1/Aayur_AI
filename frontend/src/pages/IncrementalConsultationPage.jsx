import IncrementalConsultation from '../components/IncrementalConsultation';

const IncrementalConsultationPage = ({ language = 'en' }) => {
  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>Incremental Consultation</h1>
        <p style={styles.subtitle}>
          Build your consultation step-by-step for a comprehensive analysis
        </p>
      </div>
      
      <IncrementalConsultation language={language} />
      
      <div style={styles.info}>
        <h3>Why Choose Incremental Consultation?</h3>
        <div style={styles.benefits}>
          <div style={styles.benefit}>
            <span style={styles.benefitIcon}>📝</span>
            <div>
              <h4>Step-by-Step Process</h4>
              <p>Complete your consultation at your own pace</p>
            </div>
          </div>
          <div style={styles.benefit}>
            <span style={styles.benefitIcon}>💾</span>
            <div>
              <h4>Save Progress</h4>
              <p>Your data is saved at each step</p>
            </div>
          </div>
          <div style={styles.benefit}>
            <span style={styles.benefitIcon}>🎯</span>
            <div>
              <h4>Focused Analysis</h4>
              <p>Each component analyzed separately for accuracy</p>
            </div>
          </div>
          <div style={styles.benefit}>
            <span style={styles.benefitIcon}>✓</span>
            <div>
              <h4>Review Before Submit</h4>
              <p>Check all information before generating report</p>
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
  header: {
    textAlign: 'center',
    marginBottom: '40px'
  },
  title: {
    margin: '0 0 12px 0',
    fontSize: '32px',
    color: '#333'
  },
  subtitle: {
    margin: 0,
    fontSize: '16px',
    color: '#666'
  },
  info: {
    maxWidth: '800px',
    margin: '40px auto 0',
    padding: '30px',
    backgroundColor: 'white',
    borderRadius: '12px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
  },
  benefits: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '20px',
    marginTop: '20px'
  },
  benefit: {
    display: 'flex',
    gap: '16px',
    padding: '16px',
    backgroundColor: '#f9f9f9',
    borderRadius: '8px'
  },
  benefitIcon: {
    fontSize: '32px'
  }
};

export default IncrementalConsultationPage;
