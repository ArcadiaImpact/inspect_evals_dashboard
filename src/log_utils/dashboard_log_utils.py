import streamlit as st
from inspect_evals_dashboard_schema import DashboardLog


def dashboard_log_hash_func(obj: DashboardLog) -> str:
    # Streamlit raises a UnhashableParamError since it does not know
    # how to hash DashboardLog. Here we define a custom hash function
    # that uses run_id to uniquely identify the object.
    return obj.eval.run_id


@st.cache_data(hash_funcs={DashboardLog: dashboard_log_hash_func})
def get_metrics(log: DashboardLog, exclude: list = ["stderr", "var"]) -> set[str]:
    task_metrics = set()
    for score in log.results.scores:
        metrics = {k: v for k, v in score.metrics.items() if k not in exclude}
        task_metrics.update(metrics.keys())
    return task_metrics
