import json
from typing import Any

import streamlit as st
from inspect_evals_dashboard_schema import DashboardLog

from src.log_utils.dashboard_log_utils import get_all_metrics
from src.plots.bar import create_bar_chart
from src.plots.cutoff_scatter import create_cutoff_scatter
from src.plots.pairwise import create_pairwise_analysis_table
from src.plots.plot_utils import highlight_confidence_intervals


def render_page(eval_logs: list[DashboardLog], default_values: dict[str, dict[str, str]]):
    st.subheader("Naive cross-model comparison")
    st.markdown("""
                Graphs in this section compare how different AI models perform on the same task. We call this a "naive" comparison because it uses simple averages to compare models, which doesn't tell us if one model is statistically significantly better than another. For more reliable comparisons, check out the next section. To get more accurate scores, we evaluate each sample in a dataset multiple times using the epochs feature in Inspect AI.
                """
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        naive_task_name = st.selectbox(
            "Evaluation/task",
            sorted(set(log.eval.task for log in eval_logs)),
            index=0,
            format_func=lambda option: option.removeprefix("inspect_evals/"),
            help="Name of the evaluation and the task",
            label_visibility="visible",
            key="cross_model_comparison_task_name",
        )

    naive_logs: list[DashboardLog] = [log for log in eval_logs if log.eval.task == naive_task_name]

    with col2:
        model_provider = st.selectbox(
            "Model provider",
            sorted(set(log.model_metadata.provider for log in naive_logs)),
            index=None,
            help="Name of the model developer company",
            label_visibility="visible",
            key="cross_model_comparison_model_provider",
        )

    naive_logs: list[DashboardLog] = [
        log
        for log in naive_logs
        if log.model_metadata.provider == model_provider or model_provider is None
    ]

    with col3:
        model_family = st.selectbox(
            "Model family",
            sorted(set(log.model_metadata.family for log in naive_logs)),
            index=None,
            help="Name of the model family",
            label_visibility="visible",
            key="cross_model_comparison_model_family",
        )

    naive_logs: list[DashboardLog] = [
        log
        for log in naive_logs
        if log.model_metadata.family == model_family or model_family is None
    ]

    # Get available metrics from filtered logs
    task_metrics: list[str] = sorted(set().union(*[get_all_metrics(log) for log in naive_logs]))
    
    try:
        metric_index: int = task_metrics.index(default_values[naive_task_name]["default_metric"])
    except Exception:
        metric_index = 0

    with col4:
        metric = st.selectbox(
            "Metric",
            task_metrics,
            index=metric_index,
            help="Evaluation metric",
            label_visibility="visible",
            key="cross_model_comparison_metric",
        )

    if naive_logs:
        # Display evaluation details from the first log entry
        eval_details = naive_logs[0]
        st.text("")  # Add a blank line for spacing
        st.markdown("##### Evaluation details:")
        st.markdown(f"""
                    - **Name:** {eval_details.eval_metadata.title}
                    - **Description:** {eval_details.eval_metadata.description}
                    - **ArXiv:** {eval_details.eval_metadata.arxiv}
                    - **Task path in Inspect Evals:** [{eval_details.eval_metadata.path}](https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/{eval_details.eval_metadata.path})
                    """
        )
        st.text("")  # Add a blank line for spacing

        scorer = default_values[naive_task_name]["default_scorer"]
        
        fig_bar = create_bar_chart(naive_logs, scorer, metric)
        st.plotly_chart(fig_bar)

        fig_cutoff = create_cutoff_scatter(naive_logs, scorer, metric)
        st.plotly_chart(fig_cutoff)

        st.download_button(
            label="Download chart data as JSON",
            data=json.dumps([log.model_dump(mode="json") for log in naive_logs]),
            file_name="eval_logs.json",
            mime="application/json",
        )

    st.text("")  # Add a blank line for spacing
    st.divider()
    st.subheader("Pairwise analysis (unpaired)")
    st.markdown("""
                Here we compare two models directly by specifying one model as the baseline and the other as the test model across all evaluations in this group. We use their eval score and standard errors to test their difference for statistical significance. We highlight the cells where the confidence interval is in the positive or negative range signaling that the test model is statistically significantly better or worse compared to the baseline model.
                """
    )

    col5, col6, col7 = st.columns(3)

    with col5:
        model_name = st.selectbox(
            "Model name",
            sorted(set(log.eval.model for log in eval_logs)),
            index=0,
            format_func=lambda option: option.split("/")[-1],
            help="Name of the model to compare against",
            label_visibility="visible",
            key="pairwise_analysis_model_name",
        )

    with col6:
        baseline_name = st.selectbox(
            "Baseline model name",
            sorted(set(log.eval.model for log in eval_logs)),
            index=1,
            format_func=lambda option: option.split("/")[-1],
            help="Name of the baseline model to compare against",
            label_visibility="visible",
            key="pairwise_analysis_baseline_name",
        )

    pairwise_logs = [log for log in eval_logs if log.eval.model in [model_name, baseline_name]]

    # Get available metrics from filtered logs
    task_metrics = sorted(set().union(*[get_all_metrics(log) for log in pairwise_logs]))

    with col7:
        pairwise_metric = st.selectbox(
            "Metric",
            sorted(task_metrics),
            index=0,
            help="Evaluation metric to use for pairwise analysis",
            label_visibility="visible",
            key="pairwise_analysis_metric",
        )

    if pairwise_logs:
        st.text("")  # Add a blank line for spacing
        pairwise_analysis_df = create_pairwise_analysis_table(
            pairwise_logs, model_name, baseline_name, pairwise_metric
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


@st.cache_data
def convert_df_to_csv(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode("utf-8")
