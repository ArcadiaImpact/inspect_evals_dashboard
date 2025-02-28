import json
import streamlit as st
from src.plots.plot_utils import highlight_confidence_intervals
from src.logs.example import dashboard_logs
from src.plots.bar import create_bar_chart
from src.plots.cutoff_scatter import create_cutoff_scatter
from src.plots.pairwise import create_pairwise_analysis_table
from src.pages.page_utils import get_metrics, convert_df_to_csv


st.title("Coding Evaluations")

st.markdown("""
            This page focuses on evaluating AI systems' coding capabilities, measuring aspects like passing tests, code quality, functionality and efficiency.
            """
)

st.subheader("Naive cross-model comparison")
st.markdown("""
            Graphs in this section compare how different AI models perform on the same task. We call this a "naive" comparison because it uses simple averages to compare models, which doesn't tell us if one model is statistically significantly better than another. For more reliable comparisons, check out the next section. To get more accurate scores, we evaluate each sample in a dataset multiple times using the epochs feature in Inspect AI.
           """
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    eval_task_name = st.selectbox(
        "Evaluation/task",
        sorted(set(log.eval.task for log in dashboard_logs)),
        index=0,
        format_func=lambda option: option.removeprefix("inspect_evals/"),
        help="Name of the evaluation and the task",
        label_visibility="visible",
    )

filtered_logs = [log for log in dashboard_logs if log.eval.task == eval_task_name]

with col2:
    model_provider = st.selectbox(
        "Model provider",
        sorted(set(log.model_metadata.provider for log in filtered_logs)),
        index=None,
        help="Name of the model developer company",
        label_visibility="visible",
    )

filtered_logs = [
    log
    for log in filtered_logs
    if log.model_metadata.provider == model_provider or model_provider is None
]

with col3:
    model_family = st.selectbox(
        "Model family",
        sorted(set(log.model_metadata.family for log in filtered_logs)),
        index=None,
        help="Name of the model family",
        label_visibility="visible",
    )

filtered_logs = [
    log
    for log in filtered_logs
    if log.model_metadata.family == model_family or model_family is None
]

# Get available metrics for selected task
# TODO: Might want to fetch metrics from all logs
task_metrics = get_metrics(filtered_logs[0], eval_task_name)

with col4:
    metric = st.selectbox(
        "Metric",
        sorted(task_metrics),
        index=0,
        help="Evaluation metric",
        label_visibility="visible",
    )

if filtered_logs:
    # Display evaluation details from the first log entry
    eval_details = filtered_logs[0]
    st.markdown("##### Evaluation details:")
    # TODO: Add a link to task path
    st.markdown(f"""
                **Name:** {eval_details.eval_metadata.title}

                **Description:** {eval_details.eval_metadata.description}

                **ArXiv:** {eval_details.eval_metadata.arxiv}
                
                **Task path in [inspect_evals](https://github.com/UKGovernmentBEIS/inspect_evals):** {eval_details.eval_metadata.path}
                """
    )
    st.text("")  # Add a blank line for spacing

    fig_bar = create_bar_chart(filtered_logs, metric)
    st.plotly_chart(fig_bar)

    fig_cutoff = create_cutoff_scatter(filtered_logs, metric)
    st.plotly_chart(fig_cutoff)

    st.download_button(
        label="Download chart data as JSON",
        data=json.dumps([log.model_dump(mode="json") for log in filtered_logs]),
        file_name="eval_logs.json",
        mime="application/json",
    )

st.divider()
st.subheader("Pairwise analysis (unpaired)")
st.markdown("""
            Here we compare two models directly by specifying one model as the baseline and the other as the test model across all evaluations in this group. We use their eval score and standard errors to test their difference for statistical significance. We highlight the cells where the confidence interval is in the positive or negative range signaling that the test model is statistically significantly better or worse compared to the baseline model.
            """
)

col5, col6, col7, col8 = st.columns(4)

with col5:
    pairwise_task_name = st.selectbox(
        "Evaluation/task",
        sorted(set(log.eval.task for log in dashboard_logs)),
        index=0,
        format_func=lambda option: option.removeprefix("inspect_evals/"),
        help="Name of the evaluation and the task",
        label_visibility="visible",
        key="pairwise_analysis_task_name",
    )

filtered_logs = [log for log in dashboard_logs if log.eval.task == pairwise_task_name]

with col6:
    model_name = st.selectbox(
        "Model name",
        sorted(set(log.eval.model for log in filtered_logs)),
        index=0,
        format_func=lambda option: option.split("/")[-1],
        help="Name of the model to compare against",
        label_visibility="visible",
        key="pairwise_analysis_model_name",
    )

with col7:
    baseline_name = st.selectbox(
        "Baseline model",
        sorted(set(log.eval.model for log in filtered_logs)),
        index=1,
        format_func=lambda option: option.split("/")[-1],
        help="Name of the baseline model to compare against",
        label_visibility="visible",
        key="pairwise_analysis_baseline_name",
    )

filtered_logs = [log for log in filtered_logs if log.eval.model in [model_name, baseline_name]]

# Get available metrics for selected task
task_metrics = get_metrics(filtered_logs[0], pairwise_task_name)

with col8:
    metric = st.selectbox(
        "Metric",
        sorted(task_metrics),
        index=0,
        help="Evaluation metric to use for pairwise analysis",
        label_visibility="visible",
        key="pairwise_analysis_metric",
    )

if filtered_logs:
    pairwise_analysis_df = create_pairwise_analysis_table(
        filtered_logs, model_name, baseline_name, metric
    )

    st.dataframe(pairwise_analysis_df.style.apply(highlight_confidence_intervals, axis=1))

    st.download_button(
        label="Download table as CSV",
        data=convert_df_to_csv(pairwise_analysis_df),
        file_name="pairwise_analysis.csv",
        mime="text/csv",
    )

# TODO: Add link to Colab notebook
st.markdown("""
            Note this is an unpaired analysis, so we don't compare question level scores. In a paired-differences tests, we'd compare how each evaluation question's score changes from one AI model to another, rather than just comparing the overall average scores, which helps us see the true performance difference by filtering out the natural variations in difficulty across different questions. To do a paired-differences test, refer to this [Colab notebook](link).
            """
)
