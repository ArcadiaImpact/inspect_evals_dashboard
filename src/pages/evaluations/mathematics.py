from src.config import load_config
from src.log_utils.load_eval_logs import get_log_paths, load_evaluation_logs
from src.pages.evaluations.template import render_page
import streamlit as st


st.title("Mathematics Evaluations")

st.markdown("""
            Mathematics evaluations test problem-solving skills ranging from basic grade school word problems to advanced competition-level mathematics, evaluate multilingual mathematical understanding across diverse languages, and measure the ability to reason about mathematics when presented in visual contexts, while also testing how these capabilities transfer across different formats, languages, and presentation modalities.
            """
)

config = load_config().evaluations.mathematics
eval_logs = load_evaluation_logs(get_log_paths(config))
render_page(eval_logs)
