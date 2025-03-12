from src.config import load_config
from src.log_utils.load_eval_logs import get_log_paths, load_evaluation_logs
from src.pages.evaluations.template import render_page
import streamlit as st


st.title("Knowledge Evaluations")

st.markdown("""
            Knowledge evaluations assess intellectual capabilities across multiple dimensions: breadth of factual knowledge in diverse domains (sciences, humanities, law); depth of understanding in specialized fields; reasoning abilities on complex problems; common sense understanding; academic proficiency at various educational levels; truthfulness when addressing potentially misleading questions; and appropriate response calibration between safe and unsafe queries. Rather than just measuring simple fact retrieval, these benchmarks evaluate how AI systems apply knowledge, reason through complex problems, avoid common misconceptions, and integrate understanding across different domains and tasks.
            """
)

config = load_config()["evaluations"]["knowledge"]
eval_logs = load_evaluation_logs(get_log_paths(config))
render_page(eval_logs)
