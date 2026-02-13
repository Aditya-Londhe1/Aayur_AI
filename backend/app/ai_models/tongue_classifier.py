# backend/app/ai_models/tongue_classifier.py
import torch
import torch.nn as nn
import torch.nn.functional as F
from app.ai_models.tongue_explainability import (
    TongueGradCAM,
    generate_explanation,
    image_to_base64
)


from PIL import Image
import numpy as np
import cv2
from typing import Dict, Any, Tuple
import os
import logging

logger = logging.getLogger(__name__)

class TongueClassifier(nn.Module):
    """Advanced CNN for tongue analysis"""
    
    def __init__(self, num_classes: int = 7):
        super().__init__()
        
        # Feature extractor
        self.features = nn.Sequential(
            # Block 1
            nn.Conv2d(3, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            # Block 2
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.Conv2d(128, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            # Block 3
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.Conv2d(256, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.Conv2d(256, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            # Block 4
            nn.Conv2d(256, 512, kernel_size=3, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True),
            nn.Conv2d(512, 512, kernel_size=3, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True),
            nn.Conv2d(512, 512, kernel_size=3, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
        )
        
        # Attention mechanism
        self.attention = nn.Sequential(
            nn.Conv2d(512, 512, kernel_size=1),
            nn.Sigmoid()
        )
        
        # Classifier heads
        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool2d((7, 7)),
            nn.Flatten(),
            nn.Linear(512 * 7 * 7, 4096),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(4096, 4096),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(4096, num_classes)
        )
        
        # Specialized heads for Ayurvedic features
        self.coating_head = nn.Linear(512 * 7 * 7, 5)  # coating types
        self.color_head = nn.Linear(512 * 7 * 7, 6)    # color analysis
        self.texture_head = nn.Linear(512 * 7 * 7, 4)  # texture analysis
        self.cracks_head = nn.Linear(512 * 7 * 7, 3)   # cracks detection
        self.swelling_head = nn.Linear(512 * 7 * 7, 3) # swelling detection
        
    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        features = self.features(x)                 # [B, 512, H, W]

        attention_map = self.attention(features)
        attended_features = features * attention_map

    # Let classifier handle pooling
        main_output = self.classifier(attended_features)

        pooled = F.adaptive_avg_pool2d(attended_features, (7, 7))
        flattened = torch.flatten(pooled, 1)
        coating = self.coating_head(flattened)
        color = self.color_head(flattened)
        texture = self.texture_head(flattened)
        cracks = self.cracks_head(flattened)
        swelling = self.swelling_head(flattened)
        
        return {
            'main': main_output,
            'coating': coating,
            'color': color,
            'texture': texture,
            'cracks': cracks,
            'swelling': swelling,
            'attention_map': attention_map
        }

class TongueAnalysisService:
    """Service for tongue image analysis"""
    
    def __init__(self, model_path: str = None, device: str = None):
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self.load_model(model_path)
        self.model = self.model.float()

        self.class_names = [
            'normal', 'vata_imbalance', 'pitta_imbalance', 'kapha_imbalance',
            'vata_pitta', 'vata_kapha', 'pitta_kapha'
        ]
        
        # Ayurvedic knowledge mapping
        self.ayurvedic_mapping = {
            'normal': {'dosha': 'balanced', 'confidence': 0.9},
            'vata_imbalance': {'dosha': 'vata', 'confidence': 0.85},
            'pitta_imbalance': {'dosha': 'pitta', 'confidence': 0.85},
            'kapha_imbalance': {'dosha': 'kapha', 'confidence': 0.85},
            'vata_pitta': {'dosha': 'vata_pitta', 'confidence': 0.8},
            'vata_kapha': {'dosha': 'vata_kapha', 'confidence': 0.8},
            'pitta_kapha': {'dosha': 'pitta_kapha', 'confidence': 0.8},
        }
        
        logger.info(f"TongueAnalysisService initialized on {self.device}")
    
    def load_model(self, model_path: str = None) -> TongueClassifier:
        """Load trained model"""
        model = TongueClassifier()
        
        if model_path and os.path.exists(model_path):
            try:
                state_dict = torch.load(model_path, map_location=self.device)
                model.load_state_dict(state_dict)
                logger.info(f"Loaded model from {model_path}")
            except Exception as e:
                logger.warning(f"Could not load model from {model_path}: {e}")
                logger.info("Using randomly initialized model")
        else:
            logger.info("Using randomly initialized model")
        
        model.to(self.device)
        model.eval()
        return model
    
    def preprocess_image(self, image: Image.Image) -> torch.Tensor:
        """Preprocess tongue image for model"""
        # Resize
        image = image.resize((224, 224))
        
        # Convert to numpy array
        img_array = np.array(image, dtype=np.float32) / 255.0
        
        # Normalize (ImageNet stats)
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        img_array = (img_array - mean) / std
        
        # Convert to tensor and add batch dimension
        img_tensor = (
        torch.from_numpy(img_array)
        .permute(2, 0, 1)
        .unsqueeze(0)
        .float()
        )

        return img_tensor.to(self.device)
    
    def extract_features(self, image: Image.Image) -> Dict[str, Any]:
        """Extract Ayurvedic features from tongue image"""
        try:
            # Convert to OpenCV format for traditional CV
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Color analysis in HSV space
            hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
            
            # Calculate color statistics
            hue_mean = np.mean(hsv[:, :, 0])
            saturation_mean = np.mean(hsv[:, :, 1])
            value_mean = np.mean(hsv[:, :, 2])
            
            # Determine dominant color
            if value_mean < 50:
                dominant_color = "pale"
            elif hue_mean < 30:
                dominant_color = "red"
            elif saturation_mean < 50:
                dominant_color = "white"
            else:
                dominant_color = "normal"
            
            # Edge detection for cracks
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            crack_density = np.sum(edges > 0) / edges.size
            
            # Texture analysis using LBP (simplified)
            texture_score = np.std(gray)
            
            # Coating detection (simplified)
            # Bright areas indicate coating
            bright_areas = np.sum(cv_image > 200) / cv_image.size
            
            features = {
                'color_hue': float(hue_mean),
                'color_saturation': float(saturation_mean),
                'color_brightness': float(value_mean),
                'dominant_color': dominant_color,
                'crack_density': float(crack_density),
                'texture_score': float(texture_score),
                'coating_score': float(bright_areas),
                'has_cracks': crack_density > 0.01,
                'has_coating': bright_areas > 0.1,
                'is_swollen': texture_score < 20  # Simplified
            }
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting features: {e}")
            return {}
    
    def analyze(self, image: Image.Image) -> Dict[str, Any]:
        """Complete tongue analysis"""
        try:
        # Preprocess
            img_tensor = self.preprocess_image(image)

        # Run model
            with torch.no_grad():
                outputs = self.model(img_tensor)

        # Get predictions
            main_pred = torch.softmax(outputs['main'], dim=1)[0]
            class_idx = int(torch.argmax(main_pred).item())
            confidence = float(main_pred[class_idx].item())

        # Ayurvedic features
            coating_pred = torch.softmax(outputs['coating'], dim=1)[0]
            color_pred = torch.softmax(outputs['color'], dim=1)[0]
            texture_pred = torch.softmax(outputs['texture'], dim=1)[0]
            cracks_pred = torch.sigmoid(outputs['cracks'][0])
            swelling_pred = torch.sigmoid(outputs['swelling'][0])

        # Traditional CV features
            cv_features_raw = self.extract_features(image)

        # 🔒 make CV features JSON-safe
            cv_features = {
            k: float(v) if hasattr(v, "item") else v
            for k, v in cv_features_raw.items()
            }

        # Ayurvedic interpretation
            class_name = self.class_names[class_idx]
            ayurvedic_info = self.ayurvedic_mapping.get(class_name, {})

        # Generate detailed analysis
            analysis = {
            'classification': {
                'class': class_name,
                'confidence': confidence,
                'all_classes': {
                    name: float(main_pred[i].item())
                    for i, name in enumerate(self.class_names)
                }
            },
            'ayurvedic_interpretation': {
                'dominant_dosha': ayurvedic_info.get('dosha', 'unknown'),
                'confidence': float(ayurvedic_info.get('confidence', 0.0))
            },
            'detailed_features': {
                'coating': {
                    'type': self._interpret_coating(coating_pred),
                    'thickness': float(coating_pred[torch.argmax(coating_pred)].item()),
                    'confidence': float(torch.max(coating_pred).item())
                },
                'color': {
                    'dominant': self._interpret_color(color_pred),
                    'confidence': float(torch.max(color_pred).item()),
                    'cv_analysis': cv_features.get('dominant_color', 'unknown')
                },
                'texture': {
                    'type': self._interpret_texture(texture_pred),
                    'score': float(cv_features.get('texture_score', 0.0))
                },
                'cracks': {
                    'present': bool(cracks_pred[0].item() > 0.5),
                    'severity': float(cracks_pred[0].item()),
                    'cv_density': float(cv_features.get('crack_density', 0.0))
                },
                'swelling': {
                    'present': bool(swelling_pred[0].item() > 0.5),
                    'severity': float(swelling_pred[0].item())
                }
            },
            'cv_features': cv_features,
            'model_metadata': {
                'device': str(self.device),
                'runtime': 'GPU' if torch.cuda.is_available() else 'CPU'
            }
        }

        # Calculate dosha scores
            dosha_scores_raw = self._calculate_dosha_scores(analysis)
            analysis['dosha_scores'] = {
            k: float(v) for k, v in dosha_scores_raw.items()
            }

        # ---------------- EXPLAINABLE AI ----------------
            try:
                gradcam = TongueGradCAM(self.model)
                heatmap = gradcam.generate_heatmap(img_tensor, class_idx)
                overlay_image = gradcam.overlay_heatmap(image, heatmap)

                heatmap_base64 = image_to_base64(overlay_image)

                explanation_text = generate_explanation(
                analysis["dosha_scores"],
                analysis["cv_features"]
            )

                analysis["explainability"] = {
                "explanation_text": explanation_text,
                "heatmap_image": heatmap_base64,
                "format": "base64_png"
            }

            except Exception as e:
                logger.warning(f"Explainability failed: {e}")
                analysis["explainability"] = {
                "explanation_text": (
                    "Explainable AI visualization could not be generated, "
                    "but prediction results are valid."
                ),
                "heatmap_image": None
            }

            return analysis

        except Exception as e:
            logger.error(f"Error in tongue analysis: {e}")
        raise

    
    def _interpret_coating(self, coating_pred: torch.Tensor) -> str:
        """Interpret coating prediction"""
        coating_types = ['none', 'thin_white', 'thick_white', 'yellow', 'brown']
        idx = torch.argmax(coating_pred).item()
        return coating_types[idx]
    
    def _interpret_color(self, color_pred: torch.Tensor) -> str:
        """Interpret color prediction"""
        colors = ['pink', 'red', 'pale', 'white', 'yellow', 'purple']
        idx = torch.argmax(color_pred).item()
        return colors[idx]
    
    def _interpret_texture(self, texture_pred: torch.Tensor) -> str:
        """Interpret texture prediction"""
        textures = ['smooth', 'rough', 'dry', 'moist']
        idx = torch.argmax(texture_pred).item()
        return textures[idx]
    
    def _calculate_dosha_scores(self, analysis: Dict[str, Any]) -> Dict[str, float]:
        """Calculate dosha scores from analysis"""
        # Base scores
        scores = {'vata': 0.0, 'pitta': 0.0, 'kapha': 0.0}
        
        # Color-based scoring
        color = analysis['detailed_features']['color']['dominant']
        if color in ['pale', 'white']:
            scores['vata'] += 0.3
            scores['kapha'] += 0.1
        elif color in ['red', 'yellow']:
            scores['pitta'] += 0.4
        elif color == 'purple':
            scores['vata'] += 0.2
            scores['kapha'] += 0.2
        
        # Coating-based scoring
        coating = analysis['detailed_features']['coating']['type']
        if coating == 'thick_white':
            scores['kapha'] += 0.3
        elif coating == 'yellow':
            scores['pitta'] += 0.3
        elif coating == 'brown':
            scores['vata'] += 0.2
        
        # Cracks indicate vata
        if analysis['detailed_features']['cracks']['present']:
            scores['vata'] += 0.2
        
        # Swelling indicates kapha
        if analysis['detailed_features']['swelling']['present']:
            scores['kapha'] += 0.2
        
        # Texture-based scoring
        texture = analysis['detailed_features']['texture']['type']
        if texture == 'dry':
            scores['vata'] += 0.2
        elif texture == 'moist':
            scores['kapha'] += 0.1
        
        # Normalize scores
        total = sum(scores.values())
        if total > 0:
            scores = {k: v/total for k, v in scores.items()}
        
        return scores

# Service instance (singleton)
tongue_service = TongueAnalysisService()