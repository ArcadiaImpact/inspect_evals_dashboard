import os

from src.config import load_config
from src.log_utils.load_eval_logs import get_log_paths, load_evaluation_logs

os.environ["STREAMLIT_ENV"] = "test"


def read_test_eval_logs():
    group_config = load_config().agents
    return load_evaluation_logs(get_log_paths(group_config))
