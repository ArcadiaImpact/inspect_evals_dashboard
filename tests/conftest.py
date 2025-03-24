import pytest
from src.config import load_config
from src.log_utils.load_eval_logs import get_log_paths, load_evaluation_logs


@pytest.fixture(scope="session")
def eval_logs():
    group_config = load_config().agents
    return load_evaluation_logs(get_log_paths(group_config))
