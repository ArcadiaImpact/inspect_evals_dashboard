import json

from inspect_evals_dashboard_schema import DashboardLog
from src.config import load_config
from src.log_utils.load_eval_logs import get_log_paths


def test_get_log_paths():
    group_config = load_config().agents

    log_paths = get_log_paths(group_config)

    assert len(log_paths) > 0
    assert log_paths == [
        "tests/data/test_task/1.json",
        "tests/data/test_task/2.json",
    ]


def test_load_evaluation_logs(eval_logs):
    assert len(eval_logs) > 0

    with open("tests/data/test_task/1.json") as f:
        data = json.load(f)
        # Location is set by load_evaluation_logs to the path the file was downloaded from
        data["location"] = "tests/data/test_task/1.json"
        assert DashboardLog(**data) == eval_logs[0]
