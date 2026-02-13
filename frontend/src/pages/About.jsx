import React from 'react'
import { t } from '../i18n/translations'

function About({ language }) {
  return (
    <div className="about-content fade-in">
      <div className="hero">
        <div className="ai-badge-large">
          <span className="ai-icon">🤖</span>
          <span>AI-Powered Ayurvedic Platform</span>
        </div>
        <h1>{t('about.title', language)}</h1>
        <p>{t('about.subtitle', language)}</p>
      </div>

      <div className="about-section">
        <h2>{t('about.what_is', language)}</h2>
        <p>
          Ayurveda, meaning "Science of Life," is one of the world's oldest holistic healing systems.
          Developed in India over 5,000 years ago, it's based on the belief that health and wellness
          depend on a delicate balance between mind, body, and spirit.
        </p>
        <p>
          Unlike conventional medicine that treats symptoms, Ayurveda addresses root causes by
          balancing your unique constitution (Prakriti) through personalized diet, lifestyle, and
          herbal interventions.
        </p>
      </div>

      <div className="about-section">
        <h2>{t('about.doshas', language)}</h2>
        <p>
          According to Ayurveda, three fundamental energies (doshas) govern all biological,
          psychological, and physiological functions:
        </p>

        <div className="dosha-info">
          <h3>💨 Vata (Air + Space)</h3>
          <p><strong>Qualities:</strong> Light, dry, cold, mobile, subtle, rough</p>
          <p><strong>Governs:</strong> Movement, breathing, circulation, nervous system</p>
          <p><strong>When Balanced:</strong> Creative, energetic, flexible, enthusiastic</p>
          <p><strong>When Imbalanced:</strong> Anxiety, insomnia, dry skin, constipation, irregular digestion</p>
        </div>

        <div className="dosha-info">
          <h3>🔥 Pitta (Fire + Water)</h3>
          <p><strong>Qualities:</strong> Hot, sharp, light, oily, liquid, spreading</p>
          <p><strong>Governs:</strong> Digestion, metabolism, body temperature, intelligence</p>
          <p><strong>When Balanced:</strong> Focused, courageous, warm, intelligent, good digestion</p>
          <p><strong>When Imbalanced:</strong> Inflammation, acidity, anger, skin rashes, excessive heat</p>
        </div>

        <div className="dosha-info">
          <h3>🌊 Kapha (Earth + Water)</h3>
          <p><strong>Qualities:</strong> Heavy, slow, cool, oily, smooth, stable</p>
          <p><strong>Governs:</strong> Structure, lubrication, immunity, emotional calm</p>
          <p><strong>When Balanced:</strong> Stable, compassionate, strong, patient, good immunity</p>
          <p><strong>When Imbalanced:</strong> Weight gain, lethargy, congestion, slow digestion, depression</p>
        </div>
      </div>

      <div className="about-section">
        <h2>{t('about.how_works', language)}</h2>
        <p>
          AayurAI combines traditional Ayurvedic diagnostic methods with modern AI technology
          to provide personalized health insights:
        </p>

        <div className="grid grid-2 mt-3">
          <div className="card">
            <h3>👁️ {t('feature.tongue', language)}</h3>
            <p>
              In Ayurveda, the tongue is a mirror of internal health. Our AI analyzes color,
              coating, texture, and shape to detect dosha imbalances using computer vision.
            </p>
          </div>

          <div className="card">
            <h3>💓 {t('feature.pulse', language)}</h3>
            <p>
              Nadi Pariksha (pulse diagnosis) reveals subtle energy patterns. We use signal
              processing to detect Vata (serpent), Pitta (frog), and Kapha (swan) pulse qualities.
            </p>
          </div>

          <div className="card">
            <h3>📝 {t('feature.symptoms', language)}</h3>
            <p>
              Our NLP models correlate your symptoms with Ayurvedic diagnostic patterns,
              identifying likely conditions and dosha imbalances.
            </p>
          </div>

          <div className="card">
            <h3>🎤 {t('feature.voice', language)}</h3>
            <p>
              Voice carries acoustic biomarkers. We analyze pitch, tone, and rhythm to
              detect subtle health indicators related to dosha balance.
            </p>
          </div>
        </div>
      </div>

      <div className="about-section">
        <h2>Multi-Modal Integration</h2>
        <p>
          Unlike single-method diagnosis, AayurAI integrates multiple diagnostic modalities
          for comprehensive analysis:
        </p>
        <ul style={{ paddingLeft: '1.5rem', lineHeight: '1.8' }}>
          <li><strong>Weighted Fusion:</strong> Each modality contributes based on data quality</li>
          <li><strong>Cross-Validation:</strong> Multiple methods confirm findings</li>
          <li><strong>Confidence Scoring:</strong> Transparent reliability metrics</li>
          <li><strong>Explainable AI:</strong> Clear reasoning for every diagnosis</li>
        </ul>
      </div>

      <div className="about-section">
        <h2>Personalized Recommendations</h2>
        <p>
          Based on your dosha analysis, AayurAI provides customized recommendations:
        </p>
        <div className="grid grid-2 mt-3">
          <div>
            <h3>🍽️ Dietary Guidance</h3>
            <p>Foods to favor and avoid based on your dosha</p>
          </div>
          <div>
            <h3>🧘 Lifestyle Adjustments</h3>
            <p>Daily routines, sleep, and exercise recommendations</p>
          </div>
          <div>
            <h3>🌿 Herbal Remedies</h3>
            <p>Traditional Ayurvedic herbs for your condition</p>
          </div>
          <div>
            <h3>🧘‍♀️ Yoga & Pranayama</h3>
            <p>Specific poses and breathing exercises</p>
          </div>
        </div>
      </div>

      <div className="about-section">
        <h2>{t('about.mission', language)}</h2>
        <p>
          We believe everyone deserves access to personalized, holistic healthcare. By combining
          Ayurveda's profound understanding of human constitution with AI's analytical power,
          we're making ancient wisdom accessible, understandable, and actionable for the modern world.
        </p>
      </div>

      <div className="about-section">
        <h2>{t('about.tech_stack', language)}</h2>
        <div className="grid grid-3 mt-3">
          <div className="card text-center">
            <h3>🧠 Deep Learning</h3>
            <p>PyTorch, TensorFlow</p>
          </div>
          <div className="card text-center">
            <h3>👁️ Computer Vision</h3>
            <p>CNN, ResNet, Grad-CAM</p>
          </div>
          <div className="card text-center">
            <h3>📊 Signal Processing</h3>
            <p>FFT, HRV Analysis</p>
          </div>
          <div className="card text-center">
            <h3>💬 NLP</h3>
            <p>Transformers, BERT</p>
          </div>
          <div className="card text-center">
            <h3>🔗 Integration</h3>
            <p>Multi-modal Fusion</p>
          </div>
          <div className="card text-center">
            <h3>🌐 Web Platform</h3>
            <p>React, FastAPI</p>
          </div>
        </div>
      </div>

      <div className="card" style={{ background: 'linear-gradient(135deg, #f0f7f4 0%, #d8f3dc 100%)' }}>
        <h2 className="text-center">Important Disclaimer</h2>
        <p className="text-center" style={{ fontSize: '1.1rem', lineHeight: '1.8' }}>
          AayurAI is an educational tool designed to provide insights based on Ayurvedic principles.
          It is <strong>not a substitute for professional medical advice, diagnosis, or treatment</strong>.
          Always consult qualified healthcare practitioners (BAMS doctors, physicians) for medical concerns.
          Never disregard professional medical advice or delay seeking it because of information from AayurAI.
        </p>
      </div>
    </div>
  )
}

export default About
