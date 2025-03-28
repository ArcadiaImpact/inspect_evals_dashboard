import streamlit as st
from inspect_evals_dashboard_schema import DashboardLog
from src.config import EvaluationConfig, load_config
from src.log_utils.dashboard_log_utils import read_default_values_from_configs
from src.log_utils.load_eval_logs import get_log_paths, load_evaluation_logs
from src.pages.evaluations.template import render_page

st.title("Coding Evaluations")

st.markdown("""
            Generating, modifying, and understanding code across programming languages. These evaluations test multiple dimensions including functional correctness, problem-solving ability, code quality, language breadth, contextual understanding, security awareness, and documentation. Assessment methods include challenge datasets, unit tests, human expert review, and automated code analysis.
            """)

group_config: list[EvaluationConfig] = load_config().coding
default_values: dict[str, dict[str, str]] = read_default_values_from_configs(
    group_config
)
eval_logs: list[DashboardLog] = load_evaluation_logs(get_log_paths(group_config))
render_page(eval_logs, default_values)
