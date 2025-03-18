from src.config import load_config
from src.log_utils.load_eval_logs import get_log_paths, load_evaluation_logs
from src.pages.evaluations.template import render_page
import streamlit as st


st.title("Reasoning Evaluations")

st.markdown("""
            Reasoning evaluations assess abilities in comprehension, logical inference, common sense understanding, instruction following, and information processing from various contexts and modalities. The benchmarks test how effectively AI systems can handle challenges involving mathematics, spatial reasoning, physical understanding, and extended context information.
            """
)

config = load_config().evaluations.reasoning
eval_logs = load_evaluation_logs(get_log_paths(config))
render_page(eval_logs)
