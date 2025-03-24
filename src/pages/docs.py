import streamlit as st

st.title("Documentation")

st.markdown(
    """
    This page provides a **comprehensive guide** to our evaluation methodologies, metrics, implementation details, and best practices.

    ## **Contents**

    ### **1. Introduction**
    - [Overview](#overview)
    - [Purpose of the Dashboard](#purpose-of-the-dashboard)
    - [Who Should Use This Dashboard?](#who-should-use-this-dashboard)

    ### **2. Glossary**
    - [Basic Concepts](#basic-concepts)
    - [Inspect AI Concepts](#inspect-ai-concepts)
    - [Performance Metrics](#performance-metrics)
    - [Statistical Analysis](#statistical-analysis)

    ### **3. Implementation Details**
    - [Evaluation Pipeline](#evaluation-pipeline)
    - [Model Metadata](#model-metadata)

    ### **4. Visualization and Interpretation**
    - [Understanding the Dashboard](#understanding-the-dashboard)
        - [Pairwise Analysis](#pairwise-analysis)
            - [Significance-Based Color Coding](#significance-based-color-coding)
    - [Score Interpretation](#score-interpretation)

    ### **5. Data Access & Contribution**
    - [How to Download and Use the Data](#how-to-download-and-use-the-data)
    - [How to Contribute to the Dashboard](#how-to-contribute-to-the-dashboard)
    - [How to Cite the Dashboard](#how-to-cite-the-dashboard)

    ### **6. Frequently Asked Questions (FAQ)**
    - [How do I interpret confidence intervals?](#how-do-i-interpret-confidence-intervals)
    - [What if a model's score is not statistically significant?](#what-if-a-models-score-is-not-statistically-significant)
    - [How are models selected for evaluation?](#how-are-models-selected-for-evaluation)
    - [How to reproduce the results?](#how-to-reproduce-the-results)

    ---

    ## **1. Introduction**
    ### **Overview**
    This dashboard provides a comprehensive view of how various LLMs perform across a diverse set of evaluations from [Inspect Evals](https://github.com/UKGovernmentBEIS/inspect_evals). Built in collaboration with the [UK AISI](https://www.aisi.gov.uk/), [Arcadia Impact](https://www.arcadiaimpact.org/), and the [Vector Institute](https://vectorinstitute.ai/), it enables users to explore, compare, and analyze model performance with up-to-date results.


    ### **Purpose of the Dashboard**
    The dashboard centralizes evaluation results to support downstream analysis, benchmarking, and decision-making. It allows users to:
    - Explore results across eight evaluation categories.
    - Compare model performance through bar charts and scatter plots.
    - Perform statistical pairwise analysis of models within categories.
    - Filter results by model family, provider, and other parameters.
    - Access raw data and logs for deeper insights.
    - Reproduce results via open-source implementations.

    ### **Who Should Use This Dashboard?**
    This tool serves three primary audiences:
    - **Researchers** working on scaling laws and evaluation methodologies.
    - **Analysts** processing model performance data for decision-makers.
    - **Technical teams** conducting internal evaluations against industry benchmarks.

    ---

    ## **2. Glossary**
    ### **Basic Concepts**
    - **Evaluation/Task**: A specific benchmark used to assess model performance on a particular capability (e.g., reasoning, knowledge retrieval).
    - **Model**: An AI system being evaluated (e.g., Claude 3.5 Sonnet, GPT-4o, Llama 3.1 70B).
    - **Model Provider**: The company that developed the AI model (e.g., Anthropic, OpenAI, Meta).
    - **Model Family**: A group of related models from the same provider (e.g., Claude 3, GPT-4, Llama 3).
    - **Knowledge Cutoff Date**: The date after which the model has not been trained on new information.
    - **Un-elicited**: An evaluation where the model is not guided toward a specific output (e.g., by prompt engineering, agent scaffolding, etc.).
    - **Capability vs Propensity**: Capability evaluation assesses what an AI system can do, while propensity evaluation measures what behaviors an AI system tends to exhibit naturally.
    - **Q&A Evaluations**: Assessments that measure an AI system's ability to accurately answer questions across various domains, typically evaluating factual knowledge, reasoning, and information retrieval capabilities.
    - **Agentic Evaluations**: Assessments that measure how well an AI system can act as an agent to accomplish tasks, evaluate plans, make decisions, or perform multi-step processes that require understanding user goals and executing appropriate actions.

    ### **Inspect AI Concepts**
    - **Inspect AI**: A Python library for evaluating and improving AI models.
    - **Inspect Evals**: A collection of evaluations that are used to assess the performance of AI models written in the Inspect AI framework.
    - **Run**: A single instance of a model executing an evaluation.
    - **Sample**: An individual question or challenge in an evaluation.
    - **Scorer**: The component responsible for computing metrics from model outputs.
    - **Epochs**: Multiple evaluations of the same sample to get more accurate scores (reduce variance).

    ### **Performance Metrics**
    - **Metric**: A quantitative measure used to evaluate model performance (e.g., accuracy, F1 score).
    - **Score**: The value of a specific metric for a model on a particular task.
    - **Human Baseline**: The performance level achieved by human evaluators on the same task, used as a reference point.
    - **Accuracy**: A metric that measures how often a model provides the correct response to questions or tasks.
    - **Pass@K**: A metric commonly used in coding evaluations that measures the probability of a model correctly solving a programming problem within K generated attempts.
    - **Refusal Rate**: A metric that measures the percentage of runs where a model refuses to generate a response.

    ### **Statistical Analysis**
    - **Standard Error (SE)**: Measures the uncertainty in a model's score. Smaller values indicate more precise measurements.
    - **Confidence Interval (CI)**: A range that has a 95% probability of containing the true value of the model's performance.
    - **Z-score**: A statistical measure indicating how many standard deviations a data point is from the mean. Used to determine significance.
    - **Statistical Significance**: Indicates that observed differences between models are unlikely to be due to random chance.
    - **Score Difference (Δ)**: The difference in scores between two models, indicated as `Model - Baseline` in the pairwise comparison tables.
    - **Unpaired Pairwise Analysis**: A simpler comparison that looks at the overall scores of two models without checking how they performed on each specific question. Like comparing two students' final exam grades without looking at how they did on individual questions.
    - **Paired Pairwise Analysis**: A more detailed comparison that examines how two models performed on exactly the same questions or problems. This is like comparing how two students answered each individual question on a test, which gives a clearer picture of which one truly performed better by accounting for the varying difficulty of different questions.

    ---

    ## **3. Implementation Details**
    ### **Evaluation Pipeline**

    We use the open source implementations from [Inspect Evals](https://github.com/UKGovernmentBEIS/inspect_evals) to produce the results visualized in the dashboard. This provides a standardized framework for consistent evaluation across different models and capabilities.

    For Q&A benchmarks, we calculated the appropriate number of epochs using the methodology proposed by Miller, E. (2024) in [Adding Error Bars to Evals: A Statistical Approach to Language Model Evaluations](https://arxiv.org/pdf/2411.00640). This approach ensures statistical rigor by determining the optimal number of evaluation repetitions needed for reliable results. The specific implementation logic can be found in this [Colab Notebook](https://colab.research.google.com/drive/1N0LQcXI0YSLQdyHXBWy-qX_FMkor6dnp?usp=sharing).

    ### **Technical Infrastructure**
    Our evaluation pipeline runs on AWS infrastructure for scalability and reliability:

    - **Execution Environment**: Evaluations are run on AWS EC2 instances orchestrated by AWS Batch, allowing for the execution in a Docker-in-Docker environment (relevant for agentic evaluations).
    - **Model APIs**: We use the model provider's API when available, for open source models we use AWS Bedrock and Together API. The API provider and the API endpoint used for each run is logged in the evaluation log file as well as the hover text on the charts.
    - **Data Storage**: All evaluation results, including complete log files and view bundles, are saved to an S3 bucket for persistence and accessibility.
    - **Data Visualization**: The dashboard application fetches these log files directly from the S3 bucket and transforms them into the interactive visualizations presented in the user interface.

    For detailed information on how to interpret the specific visualizations generated from this data, refer to the [Visualization and Interpretation](#visualization-and-interpretation) section.

    ### **Model Metadata**
    We collected metadata e.g. training details, knowledge cutoff date, release date, context window size, accessibility details, pricing details from the model provider's website or other publicly available sources.

    ---

    ## **4. Visualization and Interpretation**
    ### **Understanding the Dashboard**
    - **Bar Chart**: Displays model performance scores across different models for direct comparison.
    - **Scatter Plot**: Shows model performance scores plotted against knowledge cutoff dates to visualize progress over time.
    - **Radar Chart**: Displays model performance across multiple evaluation categories simultaneously, with each axis representing a different category.
    - **Error Bars**: Visual representation of the standard error, showing the range of uncertainty in a model's score.
    - **Performance Frontier**: A line connecting the models with the highest performance across different time periods, showing the evolution of capability.

    #### **Pairwise Analysis**
    - **Baseline Model**: The reference model against which another model is being compared.
    - **Model - Baseline**: The difference in scores between the test model and the baseline model.
    - **95% Confidence Interval**: The range within which the true difference between two models is expected to lie with 95% certainty.
    - **Significantly Better/Worse**: When the confidence interval is entirely positive (better) or entirely negative (worse), indicating a statistically significant difference.
    - **Unpaired Analysis**: A comparison method that treats each model's scores as independent measurements without considering correlations in performance on specific questions.
    - **Paired-Differences Test**: A more precise comparison method that examines how each evaluation question's score changes from one model to another.

    ##### **Significance-Based Color Coding**
    - **Green**: Statistically significant improvement.
    - **Red**: Statistically significant decline.
    - **Gray**: No significant difference.

    ### **Score Interpretation**

    #### **Bar and Scatter Plots**
    - **Wide Standard Error (SE) bars**: More uncertainty in the score.
    - **Narrow SE bars**: More confidence in the score.

    #### **Unpaired/Paired Pairwise Analysis**
    - **CI range entirely positive**: Model significantly outperforms Baseline.
    - **CI range entirely negative**: Baseline significantly outperforms Model.
    - **CI range includes zero**: No statistically significant difference.

    ---

    ## **5. Data Access & Contribution**
    ### **How to Download and Use the Data**
    You can download the data from the specific charts via the download button under each chart. You can also directly access the Inspect AI EvalLog files and the view bundles from the S3 bucket by clicking on the S3 link in the expander at the bottom of the page.

    ### **How to Contribute to the Dashboard**
    We accept open source contributions via pull requests on the [Inspect Evals Dashboard GitHub repository](https://github.com/ArcadiaImpact/inspect_evals_dashboard/pulls). We currently don't have a process for accepting evaluation logs from the community.

    ### **How to Cite the Dashboard**
    Use the following format:
    ```
    @online{inspect_evals_dashboard,
        author       = {Arcadia Impact, AI Safety Engineering Taskforce},
        title        = {Inspect Evals Dashboard},
        year         = {2025},
        url          = {https://inspect-evals-dashboard.streamlit.app}
    }
    ```
    
    ---

    ## **6. Frequently Asked Questions (FAQ)**
    ### **How do I interpret confidence intervals?**
    Confidence intervals show the uncertainty in a model’s score. If a CI excludes zero, the score difference is significant.

    ### **What if a model’s score is not statistically significant?**
    It suggests that the observed difference might be due to random variation rather than a real performance gap.

    ### **How often are the models updated?**
    We aim to make results available for the latest models within a week of their release.

    ### **What's the best way to ask questions or provide feedback?**
    We recommend raising an issue on the [Inspect Evals Dashboard GitHub repository](https://github.com/ArcadiaImpact/inspect_evals_dashboard/issues).
    """
)
