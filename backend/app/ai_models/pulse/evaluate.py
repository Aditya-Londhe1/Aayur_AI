import torch
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
import json
import os
from datetime import datetime
import logging
from typing import Dict, Tuple

from app.ai_models.pulse.pulse_dataset import PulseDataset, PulseDataLoader
# from app.ai_models.pulse.pulse_model import AyurvedicPulseClassifier

logger = logging.getLogger(__name__)

class PulseEvaluator:
    """Evaluator for pulse analysis model"""
    
    def __init__(self, model_path: str, device: str = None):
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_wrapper = self._load_model(model_path)
        
    def _load_model(self, model_path: str):
        """Load trained model"""
        checkpoint = torch.load(model_path, map_location=self.device)
        
        # Determine model type from checkpoint
        if 'model_config' in checkpoint:
            config = checkpoint['model_config']
            model_type = config.get('model_type', 'bilstm')
            
            if 'PulseBiLSTM' in model_type:
                from app.ai_models.pulse.pulse_model import PulseBiLSTM
                model = PulseBiLSTM(
                    input_size=config.get('input_size', 1),
                    hidden_size=config.get('hidden_size', 128),
                    num_layers=config.get('num_layers', 2),
                    num_classes=config.get('num_classes', 4),
                    feature_dim=config.get('feature_dim', 3)
                )
            else:
                from app.ai_models.pulse.pulse_model import PulseCNNBiLSTM
                model = PulseCNNBiLSTM(
                    num_classes=config.get('num_classes', 4)
                )
        else:
            # Legacy loading
            from app.ai_models.pulse.pulse_model import PulseBiLSTM
            model = PulseBiLSTM(feature_dim=3)
        
        model.load_state_dict(checkpoint['model_state_dict'])
        model.to(self.device)
        model.eval()
        
        return model # AyurvedicPulseClassifier(model=model)
    
    def evaluate_on_dataset(self, dataloader, save_dir: str = None) -> Dict:
        """Evaluate model on a dataset"""
        all_predictions = []
        all_labels = []
        all_confidences = []
        
        self.model_wrapper.eval()
        
        with torch.no_grad():
            for batch_idx, batch in enumerate(dataloader):
                signals = batch['signal'].to(self.device)
                labels = batch['label'].to(self.device).squeeze()
                features = batch['features'].to(self.device)
                
                # Get predictions
                outputs = self.model_wrapper(signals, features)
                predictions = torch.argmax(outputs['main'], dim=1)
                confidences = torch.softmax(outputs['main'], dim=1)
                
                all_predictions.extend(predictions.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())
                all_confidences.extend(confidences.cpu().numpy())
        
        # Convert to arrays
        predictions = np.array(all_predictions)
        labels = np.array(all_labels)
        confidences = np.array(all_confidences)
        
        # Calculate metrics
        accuracy = np.mean(predictions == labels)
        
        # Detailed classification report
        class_names = ['vata', 'pitta', 'kapha', 'balanced']
        report = classification_report(
            labels, predictions, 
            target_names=class_names, 
            output_dict=True
        )
        
        # Confusion matrix
        cm = confusion_matrix(labels, predictions)
        
        # Per-class confidence analysis
        confidence_analysis = {}
        for i, class_name in enumerate(class_names):
            class_mask = labels == i
            if np.any(class_mask):
                class_confidences = confidences[class_mask, i]
                confidence_analysis[class_name] = {
                    'mean_confidence': float(np.mean(class_confidences)),
                    'std_confidence': float(np.std(class_confidences)),
                    'min_confidence': float(np.min(class_confidences)),
                    'max_confidence': float(np.max(class_confidences))
                }
        
        # Generate visualizations if save_dir provided
        if save_dir:
            os.makedirs(save_dir, exist_ok=True)
            self._plot_confusion_matrix(cm, class_names, save_dir)
            self._plot_confidence_distribution(confidences, labels, class_names, save_dir)
        
        results = {
            'accuracy': float(accuracy),
            'classification_report': report,
            'confusion_matrix': cm.tolist(),
            'confidence_analysis': confidence_analysis,
            'predictions': predictions.tolist(),
            'labels': labels.tolist(),
            'confidences': confidences.tolist(),
            'timestamp': datetime.now().isoformat()
        }
        
        return results
    
    def evaluate_single_signal(self, signal: np.ndarray, 
                              features: np.ndarray = None) -> Dict:
        """Evaluate a single pulse signal"""
        # prediction = self.model_wrapper.predict(signal, features)
        prediction = {} # Placeholder as predict method is in wrapper which we removed
        
        # Add signal statistics
        signal_stats = {
            'length': len(signal),
            'mean': float(np.mean(signal)),
            'std': float(np.std(signal)),
            'min': float(np.min(signal)),
            'max': float(np.max(signal))
        }
        
        prediction['signal_statistics'] = signal_stats
        
        return prediction
    
    def _plot_confusion_matrix(self, cm, class_names, save_dir):
        """Plot and save confusion matrix"""
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                   xticklabels=class_names, yticklabels=class_names)
        plt.title('Confusion Matrix')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        
        cm_path = os.path.join(save_dir, 'confusion_matrix.png')
        plt.tight_layout()
        plt.savefig(cm_path, dpi=300)
        plt.close()
        
        logger.info(f"Saved confusion matrix to {cm_path}")
    
    def _plot_confidence_distribution(self, confidences, labels, 
                                     class_names, save_dir):
        """Plot confidence distribution by class"""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        axes = axes.ravel()
        
        for i, class_name in enumerate(class_names):
            class_mask = labels == i
            if np.any(class_mask):
                class_confidences = confidences[class_mask, i]
                
                axes[i].hist(class_confidences, bins=20, alpha=0.7, 
                           color='skyblue', edgecolor='black')
                axes[i].axvline(np.mean(class_confidences), color='red', 
                               linestyle='--', label=f'Mean: {np.mean(class_confidences):.3f}')
                axes[i].set_title(f'{class_name} Confidence Distribution')
                axes[i].set_xlabel('Confidence')
                axes[i].set_ylabel('Frequency')
                axes[i].legend()
                axes[i].grid(True, alpha=0.3)
        
        plt.suptitle('Confidence Distributions by Class')
        plt.tight_layout()
        
        conf_path = os.path.join(save_dir, 'confidence_distributions.png')
        plt.savefig(conf_path, dpi=300)
        plt.close()
        
        logger.info(f"Saved confidence distributions to {conf_path}")
    
    def save_evaluation_results(self, results: Dict, save_path: str):
        """Save evaluation results to JSON"""
        with open(save_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Saved evaluation results to {save_path}")


def main():
    """Main evaluation function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Evaluate Pulse Analysis Model')
    parser.add_argument('--model_path', type=str, required=True,
                       help='Path to trained model checkpoint')
    parser.add_argument('--data_dir', type=str, required=True,
                       help='Path to BIDMC dataset directory')
    parser.add_argument('--output_dir', type=str, default='./evaluation_results',
                       help='Directory to save evaluation results')
    parser.add_argument('--batch_size', type=int, default=32,
                       help='Batch size for evaluation')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create output directory
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = os.path.join(args.output_dir, f'evaluation_{timestamp}')
    os.makedirs(output_dir, exist_ok=True)
    
    # Load test dataset
    logger.info("Loading test dataset...")
    _, _, test_loader = PulseDataLoader.create_loaders(
        data_dir=args.data_dir,
        batch_size=args.batch_size,
        segment_length=1000,
        sampling_rate=125,
        num_workers=4
    )
    
    # Initialize evaluator
    evaluator = PulseEvaluator(args.model_path)
    
    # Evaluate on test set
    logger.info("Evaluating model on test set...")
    results = evaluator.evaluate_on_dataset(test_loader, save_dir=output_dir)
    
    # Save results
    results_path = os.path.join(output_dir, 'evaluation_results.json')
    evaluator.save_evaluation_results(results, results_path)
    
    # Print summary
    logger.info(f"Test Accuracy: {results['accuracy']:.4f}")
    
    logger.info(f"\nEvaluation complete! Results saved to {output_dir}")


if __name__ == '__main__':
    main()