import pytest
from pytest import MonkeyPatch

from src.log_utils.load_eval_logs import get_log_paths, load_evaluation_logs
from src.config import load_config

def test_get_log_paths():
    with MonkeyPatch.context() as mp:
        config = load_config()

        group_config = config.agents

        log_paths = get_log_paths(group_config)

        assert len(log_paths) > 0
        assert log_paths[0].startswith('tests/data/')


def test_load_evaluation_logs():
    with MonkeyPatch.context() as mp:
        config = load_config()
        group_config = config.agents

        eval_logs = load_evaluation_logs(get_log_paths(group_config))

        assert len(eval_logs) > 0
        
        log = eval_logs[0]
        assert log.task_metadata.name == "pubmedqa"
        assert log.cost_estimates["total"] > 0
        assert log.eval is not None