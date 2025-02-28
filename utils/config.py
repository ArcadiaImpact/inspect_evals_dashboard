import os
import yaml
from typing import Dict, Any

def load_config() -> Dict[Any, Any]:
    """
    Load configuration from config.yaml and environment variables.
    Environment variables take precedence over yaml config.
    """
    # Get environment from ENV variable, default to 'dev'
    env = os.getenv('STREAMLIT_ENV', 'dev')
    
    # Load YAML config
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yml')
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found at: {config_path}")
    
    if env not in config:
        raise ValueError(f"Environment '{env}' not found in config.yml")
    
    return config[env]
