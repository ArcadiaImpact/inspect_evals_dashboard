from src.config import load_config
from src.log_utils.load_eval_logs import get_log_paths, load_evaluation_logs
from src.pages.evaluations.template import render_page
import streamlit as st


st.title("Agentic Evaluations")

st.markdown("""
            Agentic capabilities enable autonomous goal pursuit and decision-making without constant human guidance, while agentic AI evaluations measure how effectively these systems can decompose tasks, navigate environments, select tools, maintain goal alignment, and recover from failures through multi-step challenges requiring planning, reasoning, and adaptation.
            """
)

config = load_config().evaluations.agents
eval_logs = load_evaluation_logs(get_log_paths(config))
render_page(eval_logs)
