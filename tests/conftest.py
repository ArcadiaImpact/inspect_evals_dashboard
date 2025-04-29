import os

import pytest
from src.config import load_config
from src.log_utils.load_eval_logs import get_log_paths, load_evaluation_logs

# Set default environment variables needed for testing
os.environ.setdefault("AWS_S3_BUCKET", "test-bucket")


@pytest.fixture(scope="session", autouse=True)
def set_test_env_vars():
    """Set environment variables needed for all tests."""
    # This ensures the environment variable is set for all tests
    # even if they use monkeypatch which resets environment variables
    os.environ["AWS_S3_BUCKET"] = "test-bucket"
    os.environ["STREAMLIT_ENV"] = "test"
    yield


@pytest.fixture(scope="session")
def eval_logs():
    group_config = load_config().agents
    return load_evaluation_logs(get_log_paths(group_config))
