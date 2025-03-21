import streamlit as st

from inspect_evals_dashboard_schema import DashboardLog

from src.config import EvaluationConfig, load_config
from src.log_utils.dashboard_log_utils import read_default_values_from_configs
from src.log_utils.load_eval_logs import get_log_paths, load_evaluation_logs
from src.pages.evaluations.template import render_page


st.title("Agentic Evaluations")

st.markdown("""
            Agentic capabilities enable autonomous goal pursuit and decision-making without constant human guidance, while agentic AI evaluations measure how effectively these systems can decompose tasks, navigate environments, select tools, maintain goal alignment, and recover from failures through multi-step challenges requiring planning, reasoning, and adaptation.
            """
)

group_config: list[EvaluationConfig] = load_config().agents
default_values: dict[str, dict[str, str]] = read_default_values_from_configs(group_config)
eval_logs: list[DashboardLog] = load_evaluation_logs(get_log_paths(group_config))
render_page(eval_logs, default_values)
