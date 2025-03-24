from inspect_ai.log import EvalScore
from src.config import load_config
from src.log_utils.dashboard_log_utils import (
    get_all_metrics,
    get_scorer_by_name,
    read_default_values_from_configs,
)

from . import read_test_eval_logs


def test_read_default_values_from_configs():
    group_config = load_config().agents

    print("WAT", group_config)
    default_values = read_default_values_from_configs(group_config)

    assert default_values["inspect_evals/test_task"]["default_scorer"] == "choice"
    assert default_values["inspect_evals/test_task"]["default_metric"] == "accuracy"


def test_get_all_metrics():
    eval_logs = read_test_eval_logs()
    log = eval_logs[0]

    all_metrics = get_all_metrics(log)
    assert all_metrics == {"accuracy"}


def test_get_scorer_by_name():
    eval_logs = read_test_eval_logs()
    log = eval_logs[0]

    # Append a fake score with some fake data to test the name-getting logic
    # If the logic becomes more complex we might need to generate proper data here
    log.results.scores.append(EvalScore(name="another_choice", scorer="some_data"))

    assert get_scorer_by_name(log, "another_choice").name == "another_choice"
    assert get_scorer_by_name(log, "choice").name == "choice"
    assert (
        get_scorer_by_name(log, "not-existing").name == "choice"
    )  # should default to the first one
