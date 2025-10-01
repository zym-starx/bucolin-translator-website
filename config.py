import os
from typing import Optional
import streamlit as st


def get_config(key: str, default: str = None) -> str:
    """Get config from Streamlit secrets (cloud) or environment (local)"""
    # Try Streamlit secrets first
    try:
        if key in st.secrets:
            return st.secrets[key]
    except:
        pass
    
    # Fall back to environment variables
    value = os.getenv(key, default)
    if value is None and default is None:
        raise ValueError(f"{key} must be set in environment or Streamlit secrets")
    return value

class PublicConfig:
    """Public configuration - safe to commit to repository"""
    
    # App Info
    APP_NAME = "BUCOLIN Historical Turkish Translator"
    APP_VERSION = "1.0.0"
    
    # UI Configuration
    DEFAULT_LANGUAGE_PAIR = ("ottoman_turkish", "modern_turkish")
    MAX_TEXT_LENGTH = 5000
    
    # Mock Service Settings (for demo)
    MOCK_PROCESSING_TIME = 0.8
    MOCK_CONFIDENCE_THRESHOLD = 0.7
    
    # External Links (safe to be public)
    HUGGINGFACE_URL = "https://huggingface.co/BUCOLIN"
    UNIVERSITY_URL = "https://www.boun.edu.tr"

class SecureConfig:
    """Secure configuration - load from environment variables or Streamlit secrets"""
    
    @staticmethod
    def get_api_endpoint() -> str:
        return get_config("TRANSLATION_API_URL", "http://localhost:8000/translate")
    
    @staticmethod
    def use_mock_service() -> bool:
        return get_config("USE_MOCK_SERVICE", "true").lower() == "true"
    
    @staticmethod
    def get_admin_password() -> str:
        return get_config("ADMIN_PASSWORD")  # Required, no default
    
    @staticmethod
    def is_development() -> bool:
        return get_config("ENVIRONMENT", "development") == "development"
    
    @staticmethod
    def get_secret_key() -> str:
        return get_config("SECRET_KEY", "dev-key-change-in-production")