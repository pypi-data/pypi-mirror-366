import os
import yaml
import base64
from pathlib import Path
from typing import Optional, Dict, Any
from ..base.models import UserConfig


class ConfigManager:
    def __init__(self):
        self.config_dir = Path.home() / ".definable"
        self.config_file = self.config_dir / "config.yaml"
        self._ensure_config_dir()
    
    def _ensure_config_dir(self) -> None:
        """Ensure the config directory exists"""
        self.config_dir.mkdir(exist_ok=True)
    
    def _encode_sensitive_value(self, value: str) -> str:
        """Encode sensitive values like API keys"""
        return base64.b64encode(value.encode()).decode()
    
    def _decode_sensitive_value(self, value: str) -> str:
        """Decode sensitive values"""
        try:
            return base64.b64decode(value.encode()).decode()
        except Exception:
            # If decoding fails, assume it's already plain text (backward compatibility)
            return value
    
    def _is_sensitive_key(self, key: str) -> bool:
        """Check if a key contains sensitive information"""
        sensitive_keys = ['api_key', 'token', 'password', 'secret']
        return any(sensitive in key.lower() for sensitive in sensitive_keys)
    
    def load_config(self) -> UserConfig:
        """Load user configuration"""
        if not self.config_file.exists():
            return UserConfig()
        
        try:
            with open(self.config_file, 'r') as f:
                data = yaml.safe_load(f) or {}
            
            # Decode sensitive values
            for key, value in data.items():
                if isinstance(value, str) and self._is_sensitive_key(key):
                    data[key] = self._decode_sensitive_value(value)
            
            return UserConfig(**data)
        except Exception as e:
            raise ValueError(f"Failed to load config: {e}")
    
    def save_config(self, config: UserConfig) -> None:
        """Save user configuration"""
        data = config.dict(exclude_none=True)
        
        # Encode sensitive values
        for key, value in data.items():
            if isinstance(value, str) and self._is_sensitive_key(key):
                data[key] = self._encode_sensitive_value(value)
        
        with open(self.config_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, indent=2)
    
    def get(self, key: str) -> Optional[str]:
        """Get a configuration value"""
        config = self.load_config()
        return getattr(config, key, None)
    
    def set(self, key: str, value: str) -> None:
        """Set a configuration value"""
        config = self.load_config()
        
        # Validate that the key is a valid field
        if key not in UserConfig.__fields__:
            raise ValueError(f"Unknown config key: {key}. Valid keys: {', '.join(UserConfig.__fields__.keys())}")
        
        setattr(config, key, value)
        self.save_config(config)
    
    def delete(self, key: str) -> bool:
        """Delete a configuration value"""
        config = self.load_config()
        
        if hasattr(config, key) and getattr(config, key) is not None:
            setattr(config, key, None)
            self.save_config(config)
            return True
        return False
    
    def list_config(self) -> Dict[str, Any]:
        """List all configuration with values masked for sensitive keys"""
        config = self.load_config()
        data = config.dict(exclude_none=True)
        
        # Mask sensitive values for display
        masked_data = {}
        for key, value in data.items():
            if self._is_sensitive_key(key) and value:
                masked_data[key] = f"{'*' * (len(str(value)) - 4)}{str(value)[-4:]}" if len(str(value)) > 4 else "****"
            else:
                masked_data[key] = value
        
        return masked_data
    
    def reset(self) -> None:
        """Reset all configuration"""
        if self.config_file.exists():
            self.config_file.unlink()
    
    def get_config_file_path(self) -> str:
        """Get the path to the config file"""
        return str(self.config_file)
    
    def config_exists(self) -> bool:
        """Check if config file exists"""
        return self.config_file.exists()
    
    def get_merged_config(self, cli_args: Dict[str, Any]) -> Dict[str, Any]:
        """Get configuration with CLI args taking precedence over stored config"""
        stored_config = self.load_config().dict(exclude_none=True)
        
        # Map stored config keys to commonly used names
        key_mapping = {
            'api_key': ['api_key', 'key'],
            'default_endpoint': ['endpoint', 'url'],
            'default_name': ['name']
        }
        
        merged = {}
        
        # Start with stored config
        for config_key, value in stored_config.items():
            if value is not None:
                merged[config_key] = value
                # Also add mapped keys
                if config_key in key_mapping:
                    for mapped_key in key_mapping[config_key]:
                        merged[mapped_key] = value
        
        # Override with CLI args (excluding None values)
        for key, value in cli_args.items():
            if value is not None:
                merged[key] = value
        
        return merged