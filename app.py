import os

import plotly.io as pio  # type: ignore
import sentry_sdk
import streamlit as st
from src.config import load_config
from src.log_utils.load_eval_logs import get_log_paths, load_evaluation_logs
from src.plots.radar import create_radar_chart

SENTRY_DSN = os.environ.get("SENTRY_DSN")

st.set_page_config(
    page_title="Inspect Evals Dashboard", page_icon="🤖", layout="centered"
)

# Global styles
st.markdown(
    """
    <style>
    .stMainBlockContainer.block-container {
        max-width: 1024px;
        padding-top: 16px;
    }

    .stMainBlockContainer.block-container h1,
    .stMainBlockContainer.block-container h2,
    .stMainBlockContainer.block-container h3,
    .stMainBlockContainer.block-container h4,
    .stMainBlockContainer.block-container h5,
    .stMainBlockContainer.block-container h6 {
      padding-bottom: 6px;
    }

    .flex-center-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100%;
        width: 100%;
    }
    .header-without-anchor span {
        display: none !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# There is no official sentry/streamlit integration
# But people found some workarounds in the discussion:
# https://github.com/streamlit/streamlit/issues/3426
#
# This code might stop working in a future version
@st.cache_data()
def sentry_patch_streamlit():
    """Streamlit catches all exceptions, this monkey patch sends exceptions to Sentry."""
    import sys

    script_runner = sys.modules["streamlit.runtime.scriptrunner.exec_code"]
    original_func = script_runner.handle_uncaught_app_exception

    def sentry_patched_func(ex):
        sentry_sdk.capture_exception(ex)
        original_func(ex)

    script_runner.handle_uncaught_app_exception = sentry_patched_func


if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=os.environ.get("STREAMLIT_ENV")
        if os.environ.get("STREAMLIT_ENV")
        else "unknown",
        send_default_pii=True,
    )
    sentry_patch_streamlit()


def home_content():
    st.title("Inspect Evals Dashboard")

    st.markdown(
        """
        **A comprehensive suite for assessing various capabilities of LLMs**

        [Inspect Evals](https://github.com/UKGovernmentBEIS/inspect_evals) is a repository of community-contributed LLM evaluations for [Inspect AI](https://github.com/UKGovernmentBEIS/inspect_ai). Inspect Evals was created in collaboration by the [UK AISI](https://www.aisi.gov.uk/), [Arcadia Impact](https://www.arcadiaimpact.org/), and the [Vector Institute](https://vectorinstitute.ai/).

        This dashboard showcases how well a diverse set of LLMs perform on the evaluations implemented in Inspect Evals. Its main aim is to provide access to this data for downstream use. Our data store is continuously updated with new results as new models and evaluations are published.
        """
    )

    config = load_config()

    # Containers for the model count, eval count, and run count
    titles = [
        f"{config.total_models} Models",
        f"{config.total_tasks} Evals",
        f"{config.total_runs} Runs",
    ]
    cols = st.columns(len(titles))
    for idx, col in enumerate(cols):
        c = col.container(height=120)
        c.markdown(
            f"""
                <div class="flex-center-container">
                    <h2 class="header-without-anchor" style="padding: 18px">{titles[idx]}</h2>
                </div>
                """,
            unsafe_allow_html=True,
        )

    # Load and organize logs by category
    category_logs = {}
    for category in [
        "agents",
        "assistants",
        "coding",
        "cybersecurity",
        "knowledge",
        "mathematics",
        "multimodal",
        "reasoning",
        "safeguards",
    ]:
        category_config = getattr(config, category)
        if category_config:
            category_logs[category] = load_evaluation_logs(
                get_log_paths(category_config)
            )

    if category_logs:
        # Create and display the radar chart
        st.markdown("### Model performance overview")
        st.markdown(
            "This radar chart shows how well the selected model performs across different evaluation categories."
        )

        # Get unique model names across all categories
        all_models = set()
        for logs in category_logs.values():
            all_models.update(log.model_metadata.name for log in logs)

        # Add model selector
        selected_model = st.selectbox(
            "Select a model to view its performance",
            sorted(all_models, key=str.lower),
            help="Choose a model to see its performance across different evaluation categories",
        )

        fig_radar = create_radar_chart(category_logs, selected_model)
        st.plotly_chart(fig_radar, use_container_width=True)

        with st.expander("How is the radar chart calculated?"):
            st.write(
                """
                     Each category's score is calculated by:

                     1. Normalizing each task's score relative to all models' performance on that task (0 = worst performance, 1 = best performance)
                     2. Averaging these normalized scores across all tasks within each category

                     For example, a score of 0.8 in the "Coding" category means the model performs at 80% of the best performance achieved by any model on coding tasks.

                     The error bars show the uncertainty in the model's performance across tasks within each category.

                     This visualization helps identify which categories the model excels in compared to other models, regardless of the absolute scale of different tasks.
                     """
            )

    st.markdown(
        """
        ### We aim to serve three key audiences:
        1. Researchers who predict scaling laws and work on the science of evaluations (including those focused on visualization practices)
        2. Analysts who process model performance data for decision-makers
        3. Technical teams who run internal evaluations against industry benchmarks

        ### This dashboard lets you:
        * Explore results across nine categories of evaluations, these are:
            * Agents
            * Assistants
            * Coding
            * Cybersecurity
            * Knowledge
            * Mathematics
            * Multimodal
            * Reasoning
            * Safeguards
        * Compare model performance through bar charts and temporal scatter plots
        * Perform pairwise analysis of models across evaluations within categories
        * Filter results based on specific parameters e.g. model family, model provider
        * Access raw data and detailed evaluation logs for downstream analysis
        * Reproduce results using the open-source implementation in the Inspect Evals repository
    """
    )

    st.markdown(
        """
        ### Methodology note
        Our evaluations primarily use un-elicited results to ensure fair model comparison, employing basic agents for agentic evaluations unless otherwise specified. While this approach guarantees consistency, we acknowledge it may not demonstrate maximum potential performance.

        ### Data access & usage
        All evaluation data is freely available for download and analysis. For academic citations, please use:

        ```
        @online{inspect_evals_dashboard,
            author       = {Arcadia Impact, AI Safety Engineering Taskforce},
            title        = {Inspect Evals Dashboard},
            year         = {2025},
            url          = {https://inspect-evals-dashboard.streamlit.app}
        }
        ```
    """
    )


# Initially pio.templates.default is a name of one of the preset templates
# We pull that template, update it and then set the object as default (rather than the name)
#
# To make sure this code works correctly and isn't executed twice we check
# if the default template is a string (i.e. a name, and not an object yet)
if isinstance(pio.templates.default, str):
    template = pio.templates[pio.templates.default]
    template.layout.hoverlabel.align = "left"  # make tooltips consistently aligned
    pio.templates.default = template


home = st.Page(home_content, title="Home", icon="🏠", default=True)
docs = st.Page("src/pages/docs.py", title="Documentation", icon="📚")
changelog = st.Page("src/pages/changelog.py", title="Changelog", icon="📝")
evals_agents = st.Page("src/pages/evaluations/agents.py", title="Agents", icon="🤖")
evals_assistants = st.Page(
    "src/pages/evaluations/assistants.py", title="Assistants", icon="💬"
)
evals_coding = st.Page("src/pages/evaluations/coding.py", title="Coding", icon="💻")
evals_cybersecurity = st.Page(
    "src/pages/evaluations/cybersecurity.py", title="Cybersecurity", icon="🔒"
)
evals_knowledge = st.Page(
    "src/pages/evaluations/knowledge.py", title="Knowledge", icon="🎓"
)
evals_mathematics = st.Page(
    "src/pages/evaluations/mathematics.py", title="Mathematics", icon="➗"
)
evals_multimodal = st.Page(
    "src/pages/evaluations/multimodal.py", title="Multimodal", icon="👁️"
)
evals_reasoning = st.Page(
    "src/pages/evaluations/reasoning.py", title="Reasoning", icon="🧩"
)
evals_safeguards = st.Page(
    "src/pages/evaluations/safeguards.py", title="Safeguards", icon="🛡️"
)

pg = st.navigation(
    {
        "Evaluations": [
            evals_agents,
            evals_assistants,
            evals_coding,
            evals_cybersecurity,
            evals_knowledge,
            evals_mathematics,
            evals_multimodal,
            evals_reasoning,
            evals_safeguards,
        ],
        "Navigation": [home, docs, changelog],
    }
)
pg.run()
