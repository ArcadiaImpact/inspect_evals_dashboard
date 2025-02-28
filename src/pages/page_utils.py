import streamlit as st
from inspect_evals_scoring.process_log import DashboardLog


def get_metrics(log: DashboardLog, exclude: list = ["stderr", "var"]) -> set[str]:
    task_metrics = set()
    for score in log.results.scores:
        metrics = {k: v for k, v in score.metrics.items() if k not in exclude}
        task_metrics.update(metrics.keys())
    return task_metrics


@st.cache_data
def convert_df_to_csv(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode("utf-8")
