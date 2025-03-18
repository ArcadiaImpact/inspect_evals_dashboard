from src.config import load_config
from src.log_utils.load_eval_logs import get_log_paths, load_evaluation_logs
from src.pages.evaluations.template import render_page
import streamlit as st


st.title("Safeguards Evaluations")

st.markdown("""
            Safeguards evaluations assess the vulnerability to misuse by measuring responses to explicitly harmful requests and testing knowledge retention in sensitive domains like biosecurity and cybersecurity.
            """
)

config = load_config().safeguards
eval_logs = load_evaluation_logs(get_log_paths(config))
render_page(eval_logs)
