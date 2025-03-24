import json

from inspect_evals_dashboard_schema import DashboardLog
from src.config import load_config
from src.log_utils.load_eval_logs import get_log_paths


def test_get_log_paths():
    group_config = load_config().agents

    log_paths = get_log_paths(group_config)

    assert len(log_paths) > 0
    assert log_paths[0].startswith("tests/data/")


def test_load_evaluation_logs(eval_logs):
    assert len(eval_logs) > 0

    with open("tests/data/test_task/1.json") as f:
        data = json.load(f)
        d = DashboardLog(**data)
        assert d == eval_logs[0]
