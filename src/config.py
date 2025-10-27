"""
Phelomia Configuration Management
Centralized configuration system for the Phelomia Document AI Platform
"""

import os
from pathlib import Path
from typing import Optional
from pydantic import BaseSettings


class PhelomiaSettings(BaseSettings):
    """Configuration settings for Phelomia application"""
    
    # Model settings
    model_name: str = "HuggingFaceM4/idefics3-8b-docling"
    device: str = "auto"
    max_length: int = 1024
    
    # UI settings
    theme: str = "carbon"
    enable_chat: bool = True
    max_file_size: int = 10  # MB
    show_advanced_options: bool = False
    
    # Performance settings
    batch_size: int = 1
    num_workers: int = 2
    cache_enabled: bool = True
    
    # API settings
    api_key: Optional[str] = None
    rate_limit: int = 100  # requests per hour
    
    # Debugging
    debug: bool = False
    log_level: str = "INFO"
    
    # Paths
    data_dir: str = "data"
    logs_dir: str = "logs"
    uploads_dir: str = "assets/uploads"
    
    class Config:
        env_file = ".env"
        env_prefix = "PHELOMIA_"


# Global settings instance
settings = PhelomiaSettings()


def get_settings() -> PhelomiaSettings:
    """Get the current settings instance"""
    return settings


def update_settings(**kwargs) -> PhelomiaSettings:
    """Update settings with new values"""
    global settings
    for key, value in kwargs.items():
        if hasattr(settings, key):
            setattr(settings, key, value)
    return settings


def create_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        settings.data_dir,
        settings.logs_dir,
        settings.uploads_dir,
        "assets"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)


def get_device():
    """Get the appropriate device for model execution"""
    import torch
    
    if settings.device == "auto":
        if torch.cuda.is_available():
            return "cuda"
        elif torch.backends.mps.is_available():
            return "mps"
        else:
            return "cpu"
    
    return settings.device