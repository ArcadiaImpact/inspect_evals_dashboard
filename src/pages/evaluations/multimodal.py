import streamlit as st
from inspect_evals_dashboard_schema import DashboardLog
from src.config import EvaluationConfig, load_config
from src.log_utils.dashboard_log_utils import read_default_values_from_configs
from src.log_utils.load_eval_logs import get_log_paths, load_evaluation_logs
from src.pages.evaluations.template import render_page

st.title("Multimodal Evaluations")

st.markdown("""
            Testing an AI system's ability to process, understand, and generate content across multiple types of data simultaneously. These assessments move beyond text-only testing by incorporating diverse inputs and outputs including images, text, audio, video, and structured data.
            """)

group_config: list[EvaluationConfig] = load_config().multimodal
default_values: dict[str, dict[str, str]] = read_default_values_from_configs(
    group_config
)
eval_logs: list[DashboardLog] = load_evaluation_logs(get_log_paths(group_config))
render_page(eval_logs, default_values)
