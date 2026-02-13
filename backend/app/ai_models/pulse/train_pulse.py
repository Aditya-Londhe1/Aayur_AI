import torch
import torch.nn as nn
import torch.optim as optim
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parents[3]))

from app.ai_models.pulse.pulse_dataset import PulseDataset
from app.ai_models.pulse.pulse_model import PulseBiLSTM, PulseCNNBiLSTM
import logging
import os
import json
from datetime import datetime
from torch.utils.data import DataLoader
from tqdm import tqdm
import numpy as np
from typing import Dict

logger = logging.getLogger(__name__)

class PulseTrainer:
    """Trainer for pulse analysis model"""
    
    def __init__(self, 
                 model_dir: str = './models/pulse',
                 experiment_name: str = None):
        
        self.model_dir = model_dir
        self.experiment_name = experiment_name or f"pulse_experiment_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.experiment_dir = os.path.join(model_dir, self.experiment_name)
        
        # Create directories
        os.makedirs(self.experiment_dir, exist_ok=True)
        os.makedirs(os.path.join(self.experiment_dir, 'checkpoints'), exist_ok=True)
        os.makedirs(os.path.join(self.experiment_dir, 'logs'), exist_ok=True)
        
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {self.device}")
        
        # Metrics storage
        self.train_metrics = []
        self.val_metrics = []
        
    def train(self,
              train_loader: DataLoader,
              val_loader: DataLoader,
              model: nn.Module,
              num_epochs: int = 50,
              learning_rate: float = 0.001,
              weight_decay: float = 1e-4,
              patience: int = 10) -> nn.Module:
        """
        Train the model
        
        Returns:
            Trained model
        """
        
        model = model.to(self.device)
        
        # Loss functions
        criterion_main = nn.CrossEntropyLoss()
        criterion_aux = nn.CrossEntropyLoss()  # For auxiliary tasks
        
        # Optimizer
        optimizer = optim.AdamW(model.parameters(), 
                               lr=learning_rate, 
                               weight_decay=weight_decay)
        
        # Learning rate scheduler
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, mode='min', factor=0.5, patience=5
        )
        
        # Early stopping
        best_val_loss = float('inf')
        epochs_no_improve = 0
        best_model_state = None
        
        # Training loop
        for epoch in range(num_epochs):
            logger.info(f"Epoch {epoch+1}/{num_epochs}")
            
            # Train phase
            train_metrics = self._train_epoch(
                model, train_loader, optimizer, 
                criterion_main, criterion_aux, epoch
            )
            
            # Validation phase
            val_metrics = self._validate_epoch(
                model, val_loader, criterion_main, criterion_aux, epoch
            )
            
            # Save metrics
            self.train_metrics.append(train_metrics)
            self.val_metrics.append(val_metrics)
            
            # Check for improvement
            val_loss = val_metrics['loss']
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                epochs_no_improve = 0
                best_model_state = model.state_dict().copy()
                
                # Save best model
                self._save_checkpoint(
                    model, optimizer, epoch, 
                    val_metrics, is_best=True
                )
            else:
                epochs_no_improve += 1
            
            # Update scheduler
            scheduler.step(val_loss)
            
            # Early stopping
            if epochs_no_improve >= patience:
                logger.info(f"Early stopping at epoch {epoch+1}")
                break
            
            # Save regular checkpoint
            if (epoch + 1) % 5 == 0:
                self._save_checkpoint(
                    model, optimizer, epoch, 
                    val_metrics, is_best=False
                )
            
            # Log progress
            self._log_epoch(epoch, train_metrics, val_metrics)
        
        # Load best model
        if best_model_state is not None:
            model.load_state_dict(best_model_state)
        
        # Save final model
        self._save_final_model(model)
        
        # Save training history
        self._save_training_history()
        
        return model
    
    def _train_epoch(self, model, dataloader, optimizer, 
                    criterion_main, criterion_aux, epoch) -> Dict:
        """Train for one epoch"""
        model.train()
        total_loss = 0
        total_main_loss = 0
        total_aux_loss = 0
        
        correct_main = 0
        total_samples = 0
        
        progress_bar = tqdm(dataloader, desc=f"Training Epoch {epoch+1}")
        
        for batch_idx, batch in enumerate(progress_bar):
            # Move data to device
            signals = batch['signal'].to(self.device)
            labels = batch['label'].to(self.device).squeeze()
            features = batch['features'].to(self.device)
            
            # Forward pass
            optimizer.zero_grad()
            outputs = model(signals, features)
            
            # Calculate losses
            main_loss = criterion_main(outputs['main'], labels)
            
            # Auxiliary losses (for multi-task learning)
            rhythm_loss = criterion_aux(outputs['rhythm'], labels % 3)  # Simplified
            amplitude_loss = criterion_aux(outputs['amplitude'], labels % 3)
            speed_loss = criterion_aux(outputs['speed'], labels % 3)
            
            # Expert losses
            expert_target = torch.zeros_like(outputs['expert'])
            for i, label in enumerate(labels):
                if label.item() < 3:  # Not balanced
                    expert_target[i, label.item()] = 1.0
            
            expert_loss = nn.BCELoss()(outputs['expert'], expert_target)
            
            # Total loss (weighted sum)
            loss = (
                main_loss + 
                0.3 * rhythm_loss + 
                0.3 * amplitude_loss + 
                0.3 * speed_loss +
                0.2 * expert_loss
            )
            
            # Backward pass
            loss.backward()
            
            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            
            optimizer.step()
            
            # Update metrics
            total_loss += loss.item()
            total_main_loss += main_loss.item()
            total_aux_loss += (rhythm_loss + amplitude_loss + speed_loss + expert_loss).item()
            
            # Accuracy
            _, predicted = torch.max(outputs['main'], 1)
            correct_main += (predicted == labels).sum().item()
            total_samples += labels.size(0)
            
            # Update progress bar
            progress_bar.set_postfix({
                'loss': loss.item(),
                'acc': correct_main / total_samples
            })
        
        avg_loss = total_loss / len(dataloader)
        avg_main_loss = total_main_loss / len(dataloader)
        avg_aux_loss = total_aux_loss / len(dataloader)
        accuracy = correct_main / total_samples
        
        return {
            'loss': avg_loss,
            'main_loss': avg_main_loss,
            'aux_loss': avg_aux_loss,
            'accuracy': accuracy,
            'lr': optimizer.param_groups[0]['lr']
        }
    
    def _validate_epoch(self, model, dataloader, 
                       criterion_main, criterion_aux, epoch) -> Dict:
        """Validate for one epoch"""
        model.eval()
        total_loss = 0
        total_main_loss = 0
        
        correct_main = 0
        total_samples = 0
        
        # Confusion matrix
        num_classes = 4
        confusion_matrix = np.zeros((num_classes, num_classes), dtype=int)
        
        with torch.no_grad():
            progress_bar = tqdm(dataloader, desc=f"Validation Epoch {epoch+1}")
            
            for batch_idx, batch in enumerate(progress_bar):
                signals = batch['signal'].to(self.device)
                labels = batch['label'].to(self.device).squeeze()
                features = batch['features'].to(self.device)
                
                # Forward pass
                outputs = model(signals, features)
                
                # Calculate loss
                main_loss = criterion_main(outputs['main'], labels)
                loss = main_loss
                
                # Update metrics
                total_loss += loss.item()
                total_main_loss += main_loss.item()
                
                # Accuracy and confusion matrix
                _, predicted = torch.max(outputs['main'], 1)
                correct_main += (predicted == labels).sum().item()
                total_samples += labels.size(0)
                
                # Update confusion matrix
                for t, p in zip(labels.cpu().numpy(), predicted.cpu().numpy()):
                    confusion_matrix[t, p] += 1
                
                progress_bar.set_postfix({
                    'loss': loss.item(),
                    'acc': correct_main / total_samples
                })
        
        avg_loss = total_loss / len(dataloader)
        avg_main_loss = total_main_loss / len(dataloader)
        accuracy = correct_main / total_samples
        
        # Calculate per-class metrics
        class_metrics = {}
        for i in range(num_classes):
            tp = confusion_matrix[i, i]
            fp = confusion_matrix[:, i].sum() - tp
            fn = confusion_matrix[i, :].sum() - tp
            tn = confusion_matrix.sum() - (tp + fp + fn)
            
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
            
            class_metrics[f'class_{i}'] = {
                'precision': float(precision),
                'recall': float(recall),
                'f1': float(f1)
            }
        
        return {
            'loss': avg_loss,
            'main_loss': avg_main_loss,
            'accuracy': accuracy,
            'confusion_matrix': confusion_matrix.tolist(),
            'class_metrics': class_metrics
        }
    
    def _save_checkpoint(self, model, optimizer, epoch, 
                        metrics, is_best: bool = False):
        """Save model checkpoint"""
        if is_best:
            checkpoint_path = os.path.join(
                self.experiment_dir, 'checkpoints', 'best_model.pth'
            )
        else:
            checkpoint_path = os.path.join(
                self.experiment_dir, 'checkpoints', f'checkpoint_epoch_{epoch:03d}.pth'
            )
        
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'metrics': metrics,
            'experiment_name': self.experiment_name
        }
        
        torch.save(checkpoint, checkpoint_path)
        
        if is_best:
            logger.info(f"Saved best model to {checkpoint_path}")
    
    def _save_final_model(self, model):
        """Save final trained model"""
        model_path = os.path.join(self.experiment_dir, 'final_model.pth')
        
        # Save only model weights
        torch.save({
            'model_state_dict': model.state_dict(),
            'model_config': {
                'model_type': model.__class__.__name__,
                'input_size': getattr(model, 'input_size', 1),
                'hidden_size': getattr(model, 'hidden_size', 128),
                'num_layers': getattr(model, 'num_layers', 2),
                'num_classes': getattr(model, 'num_classes', 4)
            }
        }, model_path)
        
        logger.info(f"Saved final model to {model_path}")
    
    def _save_training_history(self):
        """Save training metrics to JSON"""
        history = {
            'train': self.train_metrics,
            'val': self.val_metrics,
            'experiment_name': self.experiment_name,
            'timestamp': datetime.now().isoformat()
        }
        
        history_path = os.path.join(self.experiment_dir, 'training_history.json')
        with open(history_path, 'w') as f:
            json.dump(history, f, indent=2)
        
        logger.info(f"Saved training history to {history_path}")
    
    def _log_epoch(self, epoch, train_metrics, val_metrics):
        """Log epoch metrics"""
        log_message = (
            f"Epoch {epoch+1}:\n"
            f"  Train - Loss: {train_metrics['loss']:.4f}, "
            f"Acc: {train_metrics['accuracy']:.4f}, "
            f"LR: {train_metrics['lr']:.6f}\n"
            f"  Val   - Loss: {val_metrics['loss']:.4f}, "
            f"Acc: {val_metrics['accuracy']:.4f}"
        )
        
        logger.info(log_message)
        
        # Also save to file
        log_path = os.path.join(self.experiment_dir, 'logs', 'training.log')
        with open(log_path, 'a') as f:
            f.write(f"{datetime.now().isoformat()} - {log_message}\n")


def main():
    """Main training function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Train Pulse Analysis Model')
    parser.add_argument('--data_dir', type=str, default='d:/AayurAI_Complete/backend/app/data_dir/pulse/bidmc-ppg-and-respiration-dataset-1.0.0',
                       help='Path to BIDMC dataset directory')
    parser.add_argument('--model_dir', type=str, default='d:/AayurAI_Complete/backend/models/pulse',
                       help='Directory to save models')
    parser.add_argument('--epochs', type=int, default=10,
                       help='Number of training epochs')
    parser.add_argument('--batch_size', type=int, default=32,
                       help='Batch size')
    parser.add_argument('--learning_rate', type=float, default=0.001,
                       help='Learning rate')
    parser.add_argument('--model_type', type=str, default='bilstm',
                       choices=['bilstm', 'cnn_bilstm'],
                       help='Model architecture')
    parser.add_argument('--experiment_name', type=str, default=None,
                       help='Experiment name')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create data loaders

    logger.info("Creating data loaders...")

    train_dataset = PulseDataset(
        data_dir=args.data_dir,
        split="train"
    )

    val_dataset = PulseDataset(
        data_dir=args.data_dir,
        split="val"
    )

    test_dataset = PulseDataset(
        data_dir=args.data_dir,
        split="test"
    )

    train_loader = DataLoader(
    train_dataset,
    batch_size=args.batch_size,
    shuffle=True,
    drop_last=True,
    num_workers=4,
    pin_memory=True
    )

    val_loader = DataLoader(
    val_dataset,
    batch_size=args.batch_size,
    shuffle=False,
    num_workers=4,
    pin_memory=True
    )

    test_loader = DataLoader(
    test_dataset,
    batch_size=args.batch_size,
    shuffle=False,
    num_workers=4,
    pin_memory=True
    )

    
    # Create model
    logger.info(f"Creating {args.model_type} model...")
    if args.model_type == 'bilstm':
        model = PulseBiLSTM(
            input_size=1,
            hidden_size=128,
            num_layers=2,
            num_classes=4,
            dropout=0.3,
            use_attention=True,
            feature_dim=3
        )
    else:  # cnn_bilstm
        model = PulseCNNBiLSTM(num_classes=4)
    
    # Create trainer
    trainer = PulseTrainer(
        model_dir=args.model_dir,
        experiment_name=args.experiment_name
    )
    
    # Train model
    logger.info("Starting training...")
    trained_model = trainer.train(
        train_loader=train_loader,
        val_loader=val_loader,
        model=model,
        num_epochs=args.epochs,
        learning_rate=args.learning_rate,
        patience=10
    )
    
    logger.info("Training completed!")


if __name__ == '__main__':
    main()