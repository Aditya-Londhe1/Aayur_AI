import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Tuple, List, Optional
import numpy as np
import logging

logger = logging.getLogger(__name__)

class PulseBiLSTM(nn.Module):
    """Bi-directional LSTM for pulse waveform analysis"""
    
    def __init__(self, 
                 input_size: int = 1,
                 hidden_size: int = 128,
                 num_layers: int = 2,
                 num_classes: int = 4,  # vata, pitta, kapha, balanced
                 dropout: float = 0.3,
                 use_attention: bool = True,
                 feature_dim: int = 0  # Added for handcrafted features
    ):
        
        super().__init__()
        
        self.feature_dim = feature_dim
        
        # Bi-LSTM for temporal pattern extraction
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            bidirectional=True,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0
        )
        
        # Attention mechanism
        self.use_attention = use_attention
        if use_attention:
            self.attention = nn.Sequential(
                nn.Linear(hidden_size * 2, hidden_size),
                nn.Tanh(),
                nn.Linear(hidden_size, 1)
            )
        
        # Fusion Layer (LSTM Context + Handcrafted Features)
        fusion_input_dim = (hidden_size * 2) + feature_dim
        self.fusion_layer = nn.Sequential(
            nn.Linear(fusion_input_dim, 64),
            nn.ReLU(),
            nn.Dropout(dropout)
        )
        
        # Auxiliary Heads (Multi-task learning)
        self.rhythm_head = nn.Linear(64, 3)     # 0=Regular, 1=Irregular, 2=Chaotic
        self.amplitude_head = nn.Linear(64, 3)  # 0=Low, 1=Medium, 2=High
        self.speed_head = nn.Linear(64, 3)      # 0=Slow, 1=Normal, 2=Fast
        
        # Main Classifier
        self.classifier = nn.Linear(64, num_classes)
        
        # Expert Rule Gating (Learnable weights for rule-based overrides)
        self.expert_gate = nn.Linear(feature_dim, num_classes) if feature_dim > 0 else None
        
        # Initialize weights
        self._initialize_weights()

    def _initialize_weights(self):
        for name, param in self.named_parameters():
            if param.dim() >= 2:
                nn.init.xavier_uniform_(param)
            else:
                nn.init.zeros_(param)

    
    def forward(self, x: torch.Tensor, features: Optional[torch.Tensor] = None) -> Dict[str, torch.Tensor]:
        """
        Pulse Feature Extraction Forward Pass

        Args:
            x: Pulse signal tensor. Shape: [batch, 1, seq_len] OR [batch, seq_len, 1]
            features: Handcrafted features. Shape: [batch, feature_dim]

        Returns:
            Dict containing main logits and auxiliary outputs
        """

        # ---------------- INPUT NORMALIZATION ----------------
        if x.dim() != 3:
            raise ValueError(
                f"Pulse signal must be 3D tensor, got shape {x.shape}"
            )

        # Ensure LSTM input = [batch, seq_len, 1]
        if x.shape[1] == 1:
            x_lstm = x.permute(0, 2, 1)   # [B, T, 1]
        elif x.shape[2] == 1:
            x_lstm = x                   # [B, T, 1]
        else:
            raise ValueError(
                f"Invalid pulse signal shape {x.shape}. "
                "Expected (batch, 1, seq_len) or (batch, seq_len, 1)"
            )
        # ----------------------------------------------------

        # ---------------- BI-LSTM ----------------
        lstm_out, _ = self.lstm(x_lstm)
        # lstm_out: [B, T, hidden_size * 2]

        # Stabilize magnitude
        lstm_out = F.layer_norm(lstm_out, lstm_out.shape[-1:])

        # ---------------- ATTENTION ----------------
        if self.use_attention:
            attention_weights = self.attention(lstm_out)      # [B, T, 1]
            attention_weights = F.softmax(attention_weights / 0.7, dim=1)

            context_vector = torch.sum(
                attention_weights * lstm_out, dim=1
            )  # [B, hidden_size * 2]
        else:
            # Fallback: last hidden states
            context_vector = torch.cat(
                [lstm_out[:, -1, :lstm_out.shape[-1] // 2],
                 lstm_out[:, 0, lstm_out.shape[-1] // 2:]],
                dim=1
            )
            attention_weights = None

        # ---------------- FUSION ----------------
        if features is not None and self.feature_dim > 0:
            if features.shape[1] != self.feature_dim:
                raise ValueError(f"Expected feature dim {self.feature_dim}, got {features.shape[1]}")
            
            fused_embedding = torch.cat([context_vector, features], dim=1)
        else:
            fused_embedding = context_vector
            
        combined_features = self.fusion_layer(fused_embedding)

        # ---------------- OUTPUTS ----------------
        main_logits = self.classifier(combined_features)
        
        # Expert gating (optional refinement)
        expert_logits = None
        if self.expert_gate is not None and features is not None:
             expert_logits = torch.sigmoid(self.expert_gate(features))
             # We could combine this, but for now we just return it for auxiliary loss
        
        # Aux heads
        rhythm_logits = self.rhythm_head(combined_features)
        amplitude_logits = self.amplitude_head(combined_features)
        speed_logits = self.speed_head(combined_features)

        return {
            "main": main_logits,
            "rhythm": rhythm_logits,
            "amplitude": amplitude_logits,
            "speed": speed_logits,
            "expert": expert_logits,
            "attention_weights": attention_weights,
            "features": context_vector
        }

    



        





class PulseCNNBiLSTM(nn.Module):
    """Hybrid CNN + Bi-LSTM for pulse analysis"""
    
    def __init__(self, num_classes: int = 4):
        super().__init__()
        
        # CNN for local feature extraction
        self.cnn = nn.Sequential(
            # Block 1
            nn.Conv1d(1, 32, kernel_size=5, padding=2),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.MaxPool1d(kernel_size=2),
            
            # Block 2
            nn.Conv1d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.MaxPool1d(kernel_size=2),
            
            # Block 3
            nn.Conv1d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.MaxPool1d(kernel_size=2),
        )
        
        # Bi-LSTM for temporal dependencies
        self.lstm = nn.LSTM(
            input_size=128,
            hidden_size=64,
            num_layers=2,
            bidirectional=True,
            batch_first=True,
            dropout=0.3
        )
        
        # Attention layer
        self.attention = nn.Sequential(
            nn.Linear(128, 64),
            nn.Tanh(),
            nn.Linear(64, 1)
        )
        
        # Classifier
        self.classifier = nn.Sequential(
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, num_classes)
        )
        
    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        # CNN feature extraction
        cnn_features = self.cnn(x)  # [batch_size, 128, seq_len/8]
        
        # Prepare for LSTM
        cnn_features = cnn_features.permute(0, 2, 1)  # [batch_size, seq_len/8, 128]
        
        # Bi-LSTM
        lstm_out, _ = self.lstm(cnn_features)
        
        # Attention
        attention_weights = self.attention(lstm_out)
        attention_weights = F.softmax(attention_weights, dim=1)
        context_vector = torch.sum(attention_weights * lstm_out, dim=1)
        
        # Classification
        output = self.classifier(context_vector)
        
        return {
            'main': output,
            'attention_weights': attention_weights,
            'features': context_vector
        }


