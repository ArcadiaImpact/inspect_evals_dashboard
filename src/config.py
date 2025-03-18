import os
import re
import yaml
from typing import Optional
import streamlit as st

from pydantic import BaseModel, field_validator

class EvaluationConfig(BaseModel):
    name: str
    default_scorer: str
    default_metric: str
    paths: list[str]

    @field_validator('paths')
    @classmethod
    def substitute_env_vars(cls, paths: list[str]) -> list[str]:
        def return_environment_variable_or_throw(m):
            if m.group(1) not in os.environ:
                raise Exception("Unable to substitute an environment variable in the config, it's not set: $" + m.group(1))
            return os.environ[m.group(1)]

        processed_paths = []
        for path in paths:
            # Look for $ENV_VAR patterns
            path = re.sub(r'\$([A-Za-z0-9_]+)', return_environment_variable_or_throw, path)
            processed_paths.append(path)

        return processed_paths


class EnvironmentConfig(BaseModel):
    agents: Optional[list[EvaluationConfig]] = []
    assistants: Optional[list[EvaluationConfig]] = []
    coding: Optional[list[EvaluationConfig]] = []
    cybersecurity: Optional[list[EvaluationConfig]] = []
    knowledge: Optional[list[EvaluationConfig]] = []
    mathematics: Optional[list[EvaluationConfig]] = []
    reasoning: Optional[list[EvaluationConfig]] = []
    safeguards: Optional[list[EvaluationConfig]] = []



@st.cache_data
def load_config() -> EnvironmentConfig:
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

