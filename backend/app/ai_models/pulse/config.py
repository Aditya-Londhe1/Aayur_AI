"""
Configuration for pulse analysis system
"""

import os
from pathlib import Path
from typing import Dict, Any
import yaml

class PulseConfig:
    """Configuration manager for pulse analysis"""
    
    # Default configuration
    DEFAULTS = {
        'model': {
            'type': 'bilstm',
            'input_size': 1,
            'hidden_size': 128,
            'num_layers': 2,
            'num_classes': 4,
            'dropout': 0.3,
            'use_attention': True,
            'feature_dim': 15
        },
        'training': {
            'batch_size': 32,
            'learning_rate': 0.001,
            'num_epochs': 50,
            'weight_decay': 1e-4,
            'patience': 10,
            'validation_split': 0.15,
            'test_split': 0.15
        },
        'dataset': {
            'segment_length': 1000,  # 8 seconds at 125Hz
            'sampling_rate': 125,
            'overlap': 0.5,
            'normalize': True,
            'augment': True,
            'min_signal_length': 500
        },
        'features': {
            'extract_time_domain': True,
            'extract_frequency_domain': True,
            'extract_nonlinear': True,
            'extract_ayurvedic': True,
            'sampling_rate': 125
        },
        'paths': {
            'models_dir': './models/pulse',
            'data_dir': './data/bidmc',
            'results_dir': './results/pulse',
            'cache_dir': './cache/pulse',
            'logs_dir': './logs/pulse'
        },
        'analysis': {
            'confidence_threshold': 0.6,
            'quality_threshold': 0.3,
            'min_peaks_required': 2,
            'enable_cache': True,
            'cache_max_age_days': 7
        },
        'ayurvedic': {
            'enable_detailed_analysis': True,
            'generate_recommendations': True,
            'include_seasonal_advice': True,
            'traditional_terminology': True
        }
    }
    
    def __init__(self, config_file: str = None):
        """Initialize configuration"""
        self.config = self.DEFAULTS.copy()
        
        if config_file and Path(config_file).exists():
            self.load_config(config_file)
        
        # Create directories
        self._create_directories()
    
    def load_config(self, config_file: str):
        """Load configuration from YAML file"""
        try:
            with open(config_file, 'r') as f:
                user_config = yaml.safe_load(f)
            
            # Merge with defaults
            self._merge_dicts(self.config, user_config)
            
            print(f"Loaded configuration from {config_file}")
            
        except Exception as e:
            print(f"Error loading config file: {e}. Using defaults.")
    
    def save_config(self, config_file: str):
        """Save configuration to YAML file"""
        try:
            Path(config_file).parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_file, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
            
            print(f"Saved configuration to {config_file}")
            
        except Exception as e:
            print(f"Error saving config file: {e}")
    
    def _merge_dicts(self, target: Dict, source: Dict):
        """Recursively merge dictionaries"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._merge_dicts(target[key], value)
            else:
                target[key] = value
    
    def _create_directories(self):
        """Create necessary directories"""
        paths = self.get('paths', {})
        
        for key, dir_path in paths.items():
            if key.endswith('_dir') and dir_path:
                Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def get_model_config(self) -> Dict:
        """Get model configuration"""
        return self.get('model', {})
    
    def get_training_config(self) -> Dict:
        """Get training configuration"""
        return self.get('training', {})
    
    def get_dataset_config(self) -> Dict:
        """Get dataset configuration"""
        return self.get('dataset', {})
    
    def get_features_config(self) -> Dict:
        """Get features configuration"""
        return self.get('features', {})
    
    def get_paths_config(self) -> Dict:
        """Get paths configuration"""
        return self.get('paths', {})
    
    def get_analysis_config(self) -> Dict:
        """Get analysis configuration"""
        return self.get('analysis', {})
    
    def get_ayurvedic_config(self) -> Dict:
        """Get Ayurvedic configuration"""
        return self.get('ayurvedic', {})
    
    def update_from_args(self, args):
        """Update configuration from command line arguments"""
        if hasattr(args, 'batch_size'):
            self.set('training.batch_size', args.batch_size)
        
        if hasattr(args, 'learning_rate'):
            self.set('training.learning_rate', args.learning_rate)
        
        if hasattr(args, 'epochs'):
            self.set('training.num_epochs', args.epochs)
        
        if hasattr(args, 'model_type'):
            self.set('model.type', args.model_type)
        
        if hasattr(args, 'data_dir'):
            self.set('paths.data_dir', args.data_dir)
        
        if hasattr(args, 'model_dir'):
            self.set('paths.models_dir', args.model_dir)


# Global configuration instance
config = PulseConfig()

# Convenience functions
def get_config() -> PulseConfig:
    return config

def get_model_config() -> Dict:
    return config.get_model_config()

def get_training_config() -> Dict:
    return config.get_training_config()

def get_dataset_config() -> Dict:
    return config.get_dataset_config()

def get_features_config() -> Dict:
    return config.get_features_config()

def get_paths_config() -> Dict:
    return config.get_paths_config()

def get_analysis_config() -> Dict:
    return config.get_analysis_config()

def get_ayurvedic_config() -> Dict:
    return config.get_ayurvedic_config()