from inspect_ai.log import EvalScore
from src.config import load_config
from src.log_utils.dashboard_log_utils import (
    get_all_metrics,
    get_scorer_by_name,
    read_default_values_from_configs,
)
from src.log_utils.load_eval_logs import get_log_paths, load_evaluation_logs


def _read_eval_logs():
    group_config = load_config().agents
    return load_evaluation_logs(get_log_paths(group_config))

def test_read_default_values_from_configs():
    group_config = load_config().agents

    default_values = read_default_values_from_configs(group_config)
    print(default_values)
    assert default_values['inspect_evals/pubmedqa']['default_scorer'] == 'choice'
    assert default_values['inspect_evals/pubmedqa']['default_metric'] == 'accuracy'


def test_get_all_metrics():
    eval_logs = _read_eval_logs()
    log = eval_logs[0]

    all_metrics = get_all_metrics(log)
    assert all_metrics == {"accuracy"}


def test_get_scorer_by_name():
    eval_logs = _read_eval_logs()
    log = eval_logs[0]

    # Append a fake score with some fake data to test the name-getting logic
    # If the logic becomes more complex we might need to generate proper data here
    log.results.scores.append(EvalScore(name="another_choice", scorer="some_data"))


    assert get_scorer_by_name(log, "another_choice").name == "another_choice"
    assert get_scorer_by_name(log, "choice").name == "choice"
    assert get_scorer_by_name(log, "not-existing").name == "choice"  # should default to the first one
