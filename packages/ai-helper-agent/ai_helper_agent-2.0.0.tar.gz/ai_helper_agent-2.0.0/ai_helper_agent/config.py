"""
Configuration management for AI Helper Agent
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path
import structlog

logger = structlog.get_logger()


class Config:
    """Configuration manager for AI Helper Agent"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "config.json"
        self.config_data = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file and environment"""
        config = {}
        
        # Load from file if exists
        config_path = Path(self.config_file)
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                logger.info("Configuration loaded from file", file=str(config_path))
            except Exception as e:
                logger.error("Failed to load config file", error=str(e), file=str(config_path))
        
        # Override with environment variables
        env_config = {
            "api_keys": {
                "groq": os.getenv("GROQ_API_KEY"),
                "openai": os.getenv("OPENAI_API_KEY"),
                "anthropic": os.getenv("ANTHROPIC_API_KEY"),
                "serper": os.getenv("SERPER_API_KEY"),
            },
            "models": {
                "default": os.getenv("DEFAULT_MODEL", "groq"),
                "fallback": os.getenv("FALLBACK_MODEL", "openai")
            },
            "security": {
                "file_access": os.getenv("FILE_ACCESS_MODE", "ask"),  # always, ask, never
                "code_execution": os.getenv("CODE_EXECUTION", "restricted")  # restricted, sandboxed, disabled
            }
        }
        
        # Merge configurations (env takes precedence)
        config.update(env_config)
        return config
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for a provider"""
        return self.config_data.get("api_keys", {}).get(provider)
    
    def get_model_config(self, key: str) -> Optional[str]:
        """Get model configuration"""
        return self.config_data.get("models", {}).get(key)
    
    def get_security_setting(self, key: str) -> Optional[str]:
        """Get security setting"""
        return self.config_data.get("security", {}).get(key)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        keys = key.split(".")
        value = self.config_data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def save_config(self) -> bool:
        """Save current configuration to file"""
        try:
            # Don't save API keys to file for security
            safe_config = self.config_data.copy()
            if "api_keys" in safe_config:
                safe_config["api_keys"] = {k: "***" for k in safe_config["api_keys"]}
            
            with open(self.config_file, 'w') as f:
                json.dump(safe_config, f, indent=2)
            
            logger.info("Configuration saved", file=self.config_file)
            return True
        except Exception as e:
            logger.error("Failed to save config", error=str(e))
            return False


# Global config instance
config = Config()
