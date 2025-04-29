import os
import re

import streamlit as st
import yaml
from pydantic import BaseModel, field_validator


class EvaluationConfig(BaseModel):
    name: str
    default_scorer: str
    default_metric: str
    paths: list[str]

    @property
    def model_names(self) -> set[str]:
        """Extract model names from paths."""
        models = set()
        for path in self.paths:
            # Extract model name from path like: s3://$AWS_S3_BUCKET/logs/prod/bbh/anthropic+claude-3-7-sonnet-20250219/...
            match = re.search(r"/logs/\w+/\w+/([^/]+)/", path)
            if match:
                models.add(match.group(1))
        return models

    @property
    def prefixed_name(self) -> str:
        return f"inspect_evals/{self.name}"

    @field_validator("paths")
    @classmethod
    def substitute_env_vars(cls, paths: list[str]) -> list[str]:
        def return_environment_variable_or_throw(m):
            var_name = m.group(1) or m.group(
                2
            )  # group(1) for $VAR, group(2) for ${VAR}
            if var_name not in os.environ:
                raise Exception(
                    "Unable to substitute an environment variable in the config, it's not set: $"
                    + var_name
                )
            return os.environ[var_name]

        processed_paths = []
        for path in paths:
            # Look for both $ENV_VAR and ${ENV_VAR} patterns
            path = re.sub(
                r"\$([A-Za-z0-9_]+)|\$\{([A-Za-z0-9_]+)\}",
                return_environment_variable_or_throw,
                path,
            )
            processed_paths.append(path)

        return processed_paths


class EnvironmentConfig(BaseModel):
    agents: list[EvaluationConfig] = []
    assistants: list[EvaluationConfig] = []
    coding: list[EvaluationConfig] = []
    cybersecurity: list[EvaluationConfig] = []
    knowledge: list[EvaluationConfig] = []
    mathematics: list[EvaluationConfig] = []
    multimodal: list[EvaluationConfig] = []
    reasoning: list[EvaluationConfig] = []
    safeguards: list[EvaluationConfig] = []

    @property
    def total_tasks(self) -> int:
        # Get unique task names across all categories
        unique_tasks = {
            task.name for field in self.model_fields for task in getattr(self, field)
        }
        return len(unique_tasks)

    @property
    def total_runs(self) -> int:
        unique_paths = set()
        for field in self.model_fields:
            for task in getattr(self, field):
                for path in task.paths:
                    unique_paths.add(path)

        return len(unique_paths)

    @property
    def total_models(self) -> int:
        # Extract all unique model names from all paths
        all_models = set()
        for field in self.model_fields:
            for task in getattr(self, field):
                all_models.update(task.model_names)

        return len(all_models)


@st.cache_data
def load_config() -> EnvironmentConfig:
    """Load evaluation logs configuration from config.yaml."""
    env = os.getenv("STREAMLIT_ENV", "dev")

    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yml")
    try:
        with open(config_path, "r") as f:
            raw_config = yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found at: {config_path}")

    if env not in raw_config:
        raise ValueError(f"Environment '{env}' not found in config.yml")

    return EnvironmentConfig.model_validate(raw_config[env]["evaluations"])
