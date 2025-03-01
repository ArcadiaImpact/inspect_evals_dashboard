import os
import yaml
from typing import Dict, Any
import streamlit as st


@st.cache_data
def load_config() -> Dict[str, Any]:
    """
    Load evaluation logs configuration from config.yaml.
    """
    env = os.getenv('STREAMLIT_ENV', 'dev')
    
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yml')
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found at: {config_path}")
    
    if env not in config:
        raise ValueError(f"Environment '{env}' not found in config.yml")
    
    return config[env]
