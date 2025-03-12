from src.config import load_config
from src.log_utils.load_eval_logs import get_log_paths, load_evaluation_logs
from src.pages.evaluations.template import render_page
import streamlit as st


st.title("Assistant Evaluations")

st.markdown("""
            AI assistants interact with humans through natural language, understanding requests, providing information, and assisting with various tasks. Assistant evaluations test how effectively AI systems understand instructions, generate appropriate responses, maintain conversation context, produce accurate information, and handle complex or ambiguous requests.
            """
)

config = load_config()["evaluations"]["assistants"]
eval_logs = load_evaluation_logs(get_log_paths(config))
render_page(eval_logs)
