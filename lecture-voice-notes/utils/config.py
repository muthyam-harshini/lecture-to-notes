"""
Configuration utility for handling environment variables and Streamlit secrets
"""
import os
import streamlit as st
from typing import Optional


def get_api_key() -> Optional[str]:
    """
    Get OpenAI API key from Streamlit secrets or environment variables.
    Priority: Streamlit secrets > environment variables
    """
    # First try Streamlit secrets (for deployment)
    try:
        if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
            return st.secrets['OPENAI_API_KEY']
    except Exception:
        pass
    
    # Fall back to environment variables (for local development)
    return os.getenv('OPENAI_API_KEY')


def get_config_value(key: str, default: any = None) -> any:
    """
    Get configuration value from Streamlit secrets or environment variables.
    """
    # First try Streamlit secrets
    try:
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    
    # Fall back to environment variables
    return os.getenv(key, default)


def is_api_key_configured() -> bool:
    """
    Check if OpenAI API key is properly configured
    """
    api_key = get_api_key()
    return api_key is not None and api_key.strip() != "" and not api_key.startswith("your_")