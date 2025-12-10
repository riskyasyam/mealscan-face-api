"""
Configuration File
Central configuration untuk Face Recognition System
"""
from pathlib import Path
from typing import Tuple
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
API_DIR = BASE_DIR / "api"
DATA_DIR = BASE_DIR / "data"
FACES_DIR = DATA_DIR / "faces"
EMBEDDINGS_DIR = DATA_DIR / "embeddings"
MODELS_DIR = BASE_DIR / "models"

# Ensure directories exist
FACES_DIR.mkdir(parents=True, exist_ok=True)
EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8001))
API_RELOAD = os.getenv("API_RELOAD", "True").lower() == "true"

# Face Recognition Settings
MODEL_NAME = os.getenv("MODEL_NAME", "antelopev2")
DETECTION_SIZE: Tuple[int, int] = (
    int(os.getenv("DETECTION_SIZE", 640)),
    int(os.getenv("DETECTION_SIZE", 640))
)
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", 0.4))

# Database Configuration (Laravel)
LARAVEL_API_URL = os.getenv("LARAVEL_API_URL", "http://localhost:8000")
LARAVEL_API_KEY = os.getenv("LARAVEL_API_KEY", "")

# Security
API_KEY = os.getenv("API_KEY", "")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

# Performance
MAX_WORKERS = int(os.getenv("MAX_WORKERS", 4))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 30))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# File Upload Settings
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
MIN_IMAGE_SIZE = (50, 50)  # Minimum width, height

# Face Recognition Settings
MIN_FACE_CONFIDENCE = 0.5  # Minimum confidence untuk face detection
MAX_FACES_PER_IMAGE = 1  # Untuk registration, hanya 1 face

# Model Settings
MODEL_PROVIDERS = ["CPUExecutionProvider"]  # Change to ["CUDAExecutionProvider"] for GPU

# Redis Cache (optional, untuk future improvement)
REDIS_ENABLED = os.getenv("REDIS_ENABLED", "False").lower() == "true"
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# Development
DEBUG = os.getenv("DEBUG", "False").lower() == "true"


class Config:
    """Configuration class"""
    
    # Paths
    BASE_DIR = BASE_DIR
    DATA_DIR = DATA_DIR
    FACES_DIR = FACES_DIR
    EMBEDDINGS_DIR = EMBEDDINGS_DIR
    MODELS_DIR = MODELS_DIR
    
    # API
    API_HOST = API_HOST
    API_PORT = API_PORT
    API_RELOAD = API_RELOAD
    
    # Face Recognition
    MODEL_NAME = MODEL_NAME
    DETECTION_SIZE = DETECTION_SIZE
    SIMILARITY_THRESHOLD = SIMILARITY_THRESHOLD
    MODEL_PROVIDERS = MODEL_PROVIDERS
    
    # Laravel
    LARAVEL_API_URL = LARAVEL_API_URL
    LARAVEL_API_KEY = LARAVEL_API_KEY
    
    # Security
    API_KEY = API_KEY
    ALLOWED_ORIGINS = ALLOWED_ORIGINS
    
    # Performance
    MAX_WORKERS = MAX_WORKERS
    REQUEST_TIMEOUT = REQUEST_TIMEOUT
    
    # Logging
    LOG_LEVEL = LOG_LEVEL
    
    # File Upload
    MAX_FILE_SIZE = MAX_FILE_SIZE
    ALLOWED_EXTENSIONS = ALLOWED_EXTENSIONS
    MIN_IMAGE_SIZE = MIN_IMAGE_SIZE
    
    # Face Recognition
    MIN_FACE_CONFIDENCE = MIN_FACE_CONFIDENCE
    MAX_FACES_PER_IMAGE = MAX_FACES_PER_IMAGE
    
    # Redis
    REDIS_ENABLED = REDIS_ENABLED
    REDIS_HOST = REDIS_HOST
    REDIS_PORT = REDIS_PORT
    REDIS_DB = REDIS_DB
    
    # Development
    DEBUG = DEBUG
    
    @classmethod
    def get_all(cls) -> dict:
        """Get all configuration as dictionary"""
        return {
            key: value
            for key, value in cls.__dict__.items()
            if not key.startswith("_") and not callable(value)
        }
    
    @classmethod
    def print_config(cls):
        """Print configuration"""
        print("=" * 50)
        print("Configuration:")
        print("=" * 50)
        for key, value in cls.get_all().items():
            # Hide sensitive data
            if "KEY" in key or "PASSWORD" in key:
                value = "***HIDDEN***"
            print(f"{key}: {value}")
        print("=" * 50)


# Export config instance
config = Config()


if __name__ == "__main__":
    # Test configuration
    config.print_config()
