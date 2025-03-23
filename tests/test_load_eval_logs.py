import pytest
from pytest import MonkeyPatch

from src.log_utils.load_eval_logs import get_log_paths
from src.config import load_config

def test_get_log_paths():
    with MonkeyPatch.context() as mp:
        mp.setenv('STREAMLIT_ENV', 'test')

        config = load_config()

        group_config = config.agents

        log_paths = get_log_paths(group_config)
        print("Log paths", log_paths)

        assert len(log_paths) > 0
        assert log_paths[0].startswith('test/data/')