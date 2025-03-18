from src.config import load_config
from src.log_utils.load_eval_logs import get_log_paths, load_evaluation_logs
from src.pages.evaluations.template import render_page
import streamlit as st


st.title("Cybersecurity Evaluations")

st.markdown("""
            Cybersecurity evaluations test practical security skills via realistic hacking challenges and capture-the-flag competitions, while also measuring fundamental cybersecurity knowledge through structured questionnaires and multiple-choice assessments. Some evaluations specifically examine potentially dangerous capabilities like vulnerability exploitation and prompt injection resistance, while others focus on incident analysis and response skills.
            """
)

config = load_config().cybersecurity
eval_logs = load_evaluation_logs(get_log_paths(config))
render_page(eval_logs)
