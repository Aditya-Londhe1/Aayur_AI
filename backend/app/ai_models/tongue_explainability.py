import torch
import torch.nn.functional as F
import numpy as np
import cv2
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class TongueGradCAM:
    """
    Grad-CAM implementation for TongueClassifier
    """

    def __init__(self, model, target_layer_name="features.29"):
        """
        target_layer_name corresponds to last Conv layer in your model
        """
        self.model = model
        self.model.eval()
        self.gradients = None
        self.activations = None

        self._register_hooks(target_layer_name)

    def _register_hooks(self, target_layer_name):
        for name, module in self.model.named_modules():
            if name == target_layer_name:
                module.register_forward_hook(self._forward_hook)
                module.register_backward_hook(self._backward_hook)
                logger.info(f"Grad-CAM hooked to layer: {name}")

    def _forward_hook(self, module, input, output):
        self.activations = output.detach()

    def _backward_hook(self, module, grad_input, grad_output):
        self.gradients = grad_output[0].detach()

    def generate_heatmap(self, input_tensor, class_index):
        """
        Generate Grad-CAM heatmap
        """
        self.model.zero_grad()

        outputs = self.model(input_tensor)
        score = outputs["main"][0, class_index]
        score.backward()

        gradients = self.gradients
        activations = self.activations

        weights = torch.mean(gradients, dim=(2, 3), keepdim=True)
        cam = torch.sum(weights * activations, dim=1).squeeze()

        cam = F.relu(cam)
        cam = cam.cpu().numpy()

        cam = cv2.resize(cam, (224, 224))
        cam = cam - np.min(cam)
        cam = cam / (np.max(cam) + 1e-8)

        return cam

    @staticmethod
    def overlay_heatmap(image: Image.Image, heatmap: np.ndarray):
        """
        Overlay heatmap on original image
        """
        image_np = np.array(image.resize((224, 224)))
        heatmap_color = cv2.applyColorMap(np.uint8(255 * heatmap), cv2.COLORMAP_JET)
        overlay = cv2.addWeighted(image_np, 0.6, heatmap_color, 0.4, 0)
        return overlay
def generate_explanation(dosha_scores: dict, cv_features: dict) -> str:
    """
    Generate human-readable explanation
    """
    dominant_dosha = max(dosha_scores, key=dosha_scores.get)

    explanation = f"The analysis indicates a dominance of {dominant_dosha} dosha. "

    if cv_features.get("has_cracks"):
        explanation += "Visible cracks on the tongue suggest dryness, which is commonly associated with Vata imbalance. "

    if cv_features.get("has_coating"):
        explanation += "Presence of tongue coating indicates digestive imbalance, often linked with Kapha or Pitta. "

    if cv_features.get("dominant_color") in ["red", "yellow"]:
        explanation += "Reddish or yellowish coloration may reflect heat-related imbalance associated with Pitta. "

    explanation += (
        "These insights are generated using explainable AI techniques and Ayurvedic rules. "
        "The system provides preventive wellness guidance and does not diagnose medical conditions."
    )

    return explanation
import base64
from io import BytesIO

def image_to_base64(image_np) -> str:
    """
    Convert numpy image (BGR or RGB) to Base64 string
    """
    if len(image_np.shape) == 3:
        image_rgb = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
    else:
        image_rgb = image_np

    pil_img = Image.fromarray(image_rgb)
    buffer = BytesIO()
    pil_img.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return encoded
