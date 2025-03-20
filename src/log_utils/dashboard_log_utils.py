from typing import Optional
import streamlit as st
from inspect_evals_dashboard_schema import DashboardLog

from config import EvaluationConfig

def strip_inspect_evals_prefix(task_name):
    prefix = "inspect_evals/"
    if task_name.startswith(prefix):
        return task_name[len(prefix):]

    return task_name

def get_default_scorer(task_name: str, eval_configs: list[EvaluationConfig]) -> Optional[str]:
    task_name_stripped = strip_inspect_evals_prefix(task_name)

    for config in eval_configs:
        if config.name == task_name_stripped:
            return config.default_scorer

    return None


def find_metrics_by_scorer(log: DashboardLog, scorer: str):
    for score in log.results.scores:
        if score.scorer == scorer:
            return score.metrics

    # Default to the 0th score
    return log.results.scores[0].metrics

def find_metrics(log: DashboardLog, eval_configs: list[EvaluationConfig]):
    return find_metrics_by_scorer(log, get_default_scorer(log.eval.task, eval_configs))


def dashboard_log_hash_func(obj: DashboardLog) -> str:
    # Streamlit raises a UnhashableParamError since it does not know
    # how to hash DashboardLog. Here we define a custom hash function
    # that uses run_id to uniquely identify the object.
    return obj.eval.run_id


@st.cache_data(hash_funcs={DashboardLog: dashboard_log_hash_func})
def get_all_metrics(log: DashboardLog, exclude: list = ["stderr", "var"]) -> set[str]:
    task_metrics = set()
    for score in log.results.scores:
        metrics = {k: v for k, v in score.metrics.items() if k not in exclude}
        task_metrics.update(metrics.keys())
    return task_metrics
