
from src.config import load_config
from src.log_utils.load_eval_logs import get_log_paths, load_evaluation_logs


def test_get_log_paths():
    group_config = load_config().agents

    log_paths = get_log_paths(group_config)

    assert len(log_paths) > 0
    assert log_paths[0].startswith('tests/data/')


def test_load_evaluation_logs():
    group_config = load_config().agents
    eval_logs = load_evaluation_logs(get_log_paths(group_config))

    assert len(eval_logs) > 0

    log = eval_logs[0]
    assert log.task_metadata.name == "pubmedqa"
    assert log.cost_estimates["total"] > 0
    assert log.eval is not None
