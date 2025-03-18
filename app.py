import streamlit as st

# TODO:
# * Add links to markdown
# * Add citation

def home_content():
    st.set_page_config(
        page_title="Inspect Evals Dashboard",
        page_icon="🤖",
        layout="wide"
    )
    st.title("Inspect Evals Dashboard")
    
    st.markdown(
        """
        **A comprehensive suite for assessing various capabilities of LLMs**

        Inspect Evals is a repository of community-contributed LLM evaluations for Inspect AI. Inspect Evals was created in collaboration by the UK AISI, Arcadia Impact, and the Vector Institute.
        
        This dashboard showcases how well a diverse set of LLMs perform on the evaluations implemented in Inspect Evals. Its main aim is to provide access to this data for downstream use. Our data store is continuously updated with new results as new models and evaluations are published.

        We aim to serve three key audiences: 
        1. researchers who predict scaling laws and work on the science of evaluations (including those focused on visualization practices); 
        2. analysts who process model performance data for decision-makers; 
        3. technical teams who run internal evaluations against industry benchmarks.
    """)

    titles = ["20 Models", "35 Evals", "127 Tasks"]
    cols = st.columns(len(titles))
    for idx, col in enumerate(cols):
        markdown = f"<h1 style='text-align: center'>{titles[idx]}</h1>"
        col.container(height=120).markdown(markdown, unsafe_allow_html=True)

    st.markdown(
        """
        ### This dashboard lets you:
        * Explore results across eight categories of evaluations
        * Compare model performance through bar charts and temporal scatter plots
        * Perform pairwise analysis of models across evaluations within categories
        * Filter results based on specific parameters e.g. model family, model provider
        * Access raw data and detailed evaluation logs for downstream analysis
        * Reproduce results using the open-source implementation in the Inspect Evals repository

        ### Methodology Note
        Our evaluations primarily use un-elicited results to ensure fair model comparison, employing basic agents for agentic evaluations unless otherwise specified. While this approach guarantees consistency, we acknowledge it may not demonstrate maximum potential performance.

        ### Data Access & Usage
        All evaluation data is freely available for download and analysis. For academic citations, please use:
        [Citation to be generated]
    """)


home = st.Page(home_content, title="Home", icon="🏠")
docs = st.Page("src/pages/docs.py", title="Documentation", icon="📚")
changelog = st.Page("src/pages/changelog.py", title="Changelog", icon="📝")
evals_coding = st.Page("src/pages/evaluations/coding.py", title="Coding", icon="💻")
evals_assistants = st.Page("src/pages/evaluations/assistants.py", title="Assistants", icon="💬")
evals_cybersecurity = st.Page("src/pages/evaluations/cybersecurity.py", title="Cybersecurity", icon="🔒")
evals_safeguards = st.Page("src/pages/evaluations/safeguards.py", title="Safeguards", icon="🛡️")
evals_mathematics = st.Page("src/pages/evaluations/mathematics.py", title="Mathematics", icon="➗")
evals_reasoning = st.Page("src/pages/evaluations/reasoning.py", title="Reasoning", icon="🧩")
evals_knowledge = st.Page("src/pages/evaluations/knowledge.py", title="Knowledge", icon="🎓")
evals_agents = st.Page("src/pages/evaluations/agents.py", title="Agents", icon="🤖")

pg = st.navigation(
    {
        "Navigation": [home, docs, changelog],
        "Evaluations": [
            evals_coding,
            evals_assistants,
            evals_cybersecurity,
            evals_safeguards,
            evals_mathematics,
            evals_reasoning,
            evals_knowledge,
            evals_agents
        ]
    }
)
pg.run()
