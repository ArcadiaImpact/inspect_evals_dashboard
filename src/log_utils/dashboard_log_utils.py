import streamlit as st

from inspect_ai.log import EvalScore
from inspect_evals_dashboard_schema import DashboardLog

from src.config import EvaluationConfig


@st.cache_data(hash_funcs={DashboardLog: id, EvalScore: id})
def get_scorer_by_name(log: DashboardLog, scorer_name: str) -> EvalScore:
    try:
        return next(score for score in log.results.scores if score.name == scorer_name)
    except StopIteration:
        # Fallback to first scorer if requested one isn't found
        return log.results.scores[0]


@st.cache_data(hash_funcs={EvaluationConfig: id})
def read_default_values_from_configs(eval_configs: list[EvaluationConfig]) -> dict[str, dict[str, str]]:
    default_values: dict[str, dict[str, str]] = {}
    for config in eval_configs:
        default_values[config.prefixed_name] = {
            "default_scorer": config.default_scorer,
            "default_metric": config.default_metric
        }
    return default_values


@st.cache_data(hash_funcs={DashboardLog: id})
def get_all_metrics(log: DashboardLog, exclude: list = ["stderr", "var"]) -> set[str]:
    task_metrics = set()
    for score in log.results.scores:
        metrics = {k: v for k, v in score.metrics.items() if k not in exclude}
        task_metrics.update(metrics.keys())
    return task_metrics
