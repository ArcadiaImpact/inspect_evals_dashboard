import streamlit as st
from inspect_evals_dashboard_schema import DashboardLog
from src.config import EvaluationConfig, load_config
from src.log_utils.dashboard_log_utils import read_default_values_from_configs
from src.log_utils.load_eval_logs import get_log_paths, load_evaluation_logs
from src.pages.evaluations.template import render_page

st.title("Cybersecurity Evaluations")

st.markdown("""
            Cybersecurity evaluations assess security skills through practical hacking challenges, CTF competitions, and knowledge-based questionnaires. Some examine potentially dangerous capabilities like vulnerability exploitation and prompt injection resistance, while others focus on incident analysis and response skills.
            """)

group_config: list[EvaluationConfig] = load_config().cybersecurity
default_values: dict[str, dict[str, str]] = read_default_values_from_configs(
    group_config
)
eval_logs: list[DashboardLog] = load_evaluation_logs(get_log_paths(group_config))
render_page(eval_logs, default_values)
