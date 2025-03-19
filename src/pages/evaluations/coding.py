from src.config import load_config
from src.log_utils.load_eval_logs import get_log_paths, load_evaluation_logs
from src.pages.evaluations.template import render_page
import streamlit as st


st.title("Coding Evaluations")

st.markdown("""
            Coding evaluations measure how effectively AI systems generate, modify, and understand code across programming languages. These evaluations test functional correctness, problem-solving ability, code quality, language breadth, contextual understanding, security awareness, and documentation through methods like challenge datasets, unit tests, human review, and automated analysis.
            """
)

config = load_config().coding
eval_logs = load_evaluation_logs(get_log_paths(config))
render_page(eval_logs, config)
