import os
import yaml
from typing import Dict, Any, List, Optional
import streamlit as st

from pydantic import BaseModel, model_validator

class EvaluationConfig(BaseModel):
    name: str
    default_scorer: str
    default_metric: str
    paths: List[str]


class EnvironmentConfig(BaseModel):
    agents: Optional[List[EvaluationConfig]] = []
    assistants: Optional[List[EvaluationConfig]] = []
    coding: Optional[List[EvaluationConfig]] = []
    cybersecurity: Optional[List[EvaluationConfig]] = []
    knowledge: Optional[List[EvaluationConfig]] = []
    mathematics: Optional[List[EvaluationConfig]] = []
    reasoning: Optional[List[EvaluationConfig]] = []
    safeguards: Optional[List[EvaluationConfig]] = []



@st.cache_data
def load_config() -> Dict[str, Any]:
    """
    Load evaluation logs configuration from config.yaml.
    """
    env = os.getenv('STREAMLIT_ENV', 'dev')
    
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yml')
    try:
        with open(config_path, 'r') as f:
            raw_config = yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found at: {config_path}")
    
    if env not in raw_config:
        raise ValueError(f"Environment '{env}' not found in config.yml")
    
    return EnvironmentConfig.model_validate(raw_config[env]['evaluations'])

