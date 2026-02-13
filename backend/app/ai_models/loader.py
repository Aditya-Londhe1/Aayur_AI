import logging

logger = logging.getLogger(__name__)

class ModelLoader:
    """
    Centralized loader for AI models.
    Models are initialized once at application startup.
    """

    async def load_all_models(self):
        """
        Load all AI models required by the application.
        """
        try:
            logger.info("Starting AI model loading process...")
            
            # Load Tongue Analysis model
            logger.info("Loading Tongue Analysis model...")
            try:
                from app.ai_models.tongue_classifier import tongue_service
                _ = tongue_service  # force initialization
                logger.info("✓ Tongue Analysis model loaded successfully")
            except Exception as e:
                logger.warning(f"⚠ Tongue model lazy load failed: {e}")

            # Load Pulse Analysis model
            logger.info("Loading Pulse Analysis model...")
            try:
                from app.services.pulse_service import PulseService
                pulse_service = PulseService()
                # Try to load model if available
                try:
                    pulse_service.load_model()
                    logger.info("✓ Pulse Analysis model loaded successfully")
                except Exception as e:
                    logger.warning(f"⚠ Pulse model not found, using random weights: {e}")
            except Exception as e:
                logger.error(f"✗ Failed to initialize Pulse service: {e}")

            # Load Symptom Analysis model
            logger.info("Loading Symptom Analysis model...")
            try:
                from app.ai_models.symptom_analysis import symptom_analyzer
                success = symptom_analyzer.load_model()
                if success:
                    logger.info("✓ Symptom Analysis transformer model loaded successfully")
                else:
                    logger.info("✓ Symptom Analysis using keyword fallback (transformers unavailable)")
            except Exception as e:
                logger.error(f"✗ Failed to load Symptom Analysis: {e}")

            # Load Fusion Service
            logger.info("Loading Fusion Service...")
            try:
                from app.services.fusion_service import FusionService
                fusion_service = FusionService()
                logger.info("✓ Fusion Service loaded successfully")
            except Exception as e:
                logger.error(f"✗ Failed to load Fusion Service: {e}")

            logger.info("🎉 AI model loading process completed!")

        except Exception as e:
            logger.error(f"💥 Critical error during model loading: {e}")
            raise
            logger.error(f"Model loading failed: {e}")
            raise