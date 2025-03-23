import streamlit as st
from inspect_evals_dashboard_schema import DashboardLog
from src.config import EvaluationConfig, load_config
from src.log_utils.dashboard_log_utils import read_default_values_from_configs
from src.log_utils.load_eval_logs import get_log_paths, load_evaluation_logs
from src.pages.evaluations.template import render_page

st.title("Knowledge Evaluations")

st.markdown("""
            Knowledge evaluations assess intellectual capabilities across multiple dimensions: breadth of factual knowledge in diverse domains (sciences, humanities, law); depth of understanding in specialized fields; reasoning abilities on complex problems; common sense understanding; academic proficiency at various educational levels; truthfulness when addressing potentially misleading questions; and appropriate response calibration between safe and unsafe queries. Rather than just measuring simple fact retrieval, these benchmarks evaluate how AI systems apply knowledge, reason through complex problems, avoid common misconceptions, and integrate understanding across different domains and tasks.
            """)

group_config: list[EvaluationConfig] = load_config().knowledge
default_values: dict[str, dict[str, str]] = read_default_values_from_configs(
    group_config
)
eval_logs: list[DashboardLog] = load_evaluation_logs(get_log_paths(group_config))
render_page(eval_logs, default_values)
