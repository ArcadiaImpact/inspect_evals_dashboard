import json

import pandas as pd
import streamlit as st
from inspect_evals_dashboard_schema import DashboardLog
from src.log_utils.aws_s3_utils import (
    create_presigned_url,
    parse_s3_url_for_presigned_url,
)
from src.log_utils.dashboard_log_utils import get_all_metrics
from src.plots.bar import create_bar_chart
from src.plots.cost_scatter import create_cost_scatter
from src.plots.cutoff_scatter import create_cutoff_scatter
from src.plots.pairwise import create_pairwise_analysis_table, create_pairwise_scatter
from src.plots.plot_utils import highlight_confidence_intervals


def render_page(
    eval_logs: list[DashboardLog], default_values: dict[str, dict[str, str]]
):
    st.subheader("Naive cross-model comparison")
    st.markdown("""
                Graphs in this section compare how different AI models perform on the same task. We call this a "naive" comparison because it uses simple averages to compare models, without determining if one model is statistically significantly better than another. To get more accurate scores, we evaluate each sample in a dataset multiple times using the epochs feature in Inspect AI. For more reliable statistical comparisons between models, check out the pairwise analysis in the next section.
                """)

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

    task_filtered_logs: list[DashboardLog] = [
        log for log in eval_logs if log.eval.task == naive_task_name
    ]

    with col2:
        model_providers = st.multiselect(
            "Model providers",
            sorted(set(log.model_metadata.provider for log in task_filtered_logs)),
            default=None,
            help="Name of the model developer companies",
            label_visibility="visible",
            key="cross_model_comparison_model_provider",
        )

    provider_filtered_logs: list[DashboardLog] = [
        log
        for log in task_filtered_logs
        if log.model_metadata.provider in model_providers or not model_providers
    ]

    with col3:
        model_families = st.multiselect(
            "Model families",
            sorted(set(log.model_metadata.family for log in provider_filtered_logs)),
            default=None,
            help="Name of the model families",
            label_visibility="visible",
            key="cross_model_comparison_model_family",
        )

    family_filtered_logs: list[DashboardLog] = [
        log
        for log in provider_filtered_logs
        if log.model_metadata.family in model_families or not model_families
    ]

    # Get available metrics from filtered logs
    task_metrics: list[str] = sorted(
        set().union(*[get_all_metrics(log) for log in family_filtered_logs])
    )

    try:
        metric_index: int = task_metrics.index(
            default_values[naive_task_name]["default_metric"]
        )
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

    if family_filtered_logs:
        # Display evaluation details from the first log entry
        eval_details = family_filtered_logs[0]
        st.text("")  # Add a blank line for spacing
        st.markdown("##### Evaluation details:")
        st.markdown(f"""
                    - **Name:** {eval_details.eval_metadata.title}
                    - **Description:** {eval_details.eval_metadata.description}
                    - **ArXiv:** {eval_details.eval_metadata.arxiv}
                    - **Task path in Inspect Evals:** [{eval_details.eval_metadata.path}](https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/{eval_details.eval_metadata.path})
                    """)
        st.text("")  # Add a blank line for spacing

        scorer = default_values[naive_task_name]["default_scorer"]

        fig_bar = create_bar_chart(family_filtered_logs, scorer, metric)
        st.plotly_chart(fig_bar)

        fig_cutoff = create_cutoff_scatter(family_filtered_logs, scorer, metric)
        st.plotly_chart(fig_cutoff)

        fig_cost = create_cost_scatter(family_filtered_logs, scorer, metric)
        st.plotly_chart(fig_cost)

        st.download_button(
            label="Download chart data as JSON",
            data=json.dumps(
                [log.model_dump(mode="json") for log in family_filtered_logs]
            ),
            file_name="eval_logs.json",
            mime="application/json",
        )

    st.text("")  # Add a blank line for spacing
    st.divider()
    st.subheader("Pairwise analysis (unpaired)")
    st.markdown("""
                Here we compare two models directly by specifying one model as the baseline and the other as the test model across all evaluations in this group. We use their eval score and standard errors to test their difference for statistical significance. **We highlight the cells where the confidence interval is in the positive or negative range signaling that the test model is statistically significantly better or worse compared to the baseline model.**
                """)

    col5, col6 = st.columns(2)

    with col5:
        model_name = st.selectbox(
            "Model name",
            sorted(set(log.eval.model for log in eval_logs), key=get_model_name),
            index=0,
            format_func=get_model_name,
            help="Name of the model to compare against",
            label_visibility="visible",
            key="pairwise_analysis_model_name",
        )

    with col6:
        baseline_name = st.selectbox(
            "Baseline model name",
            sorted(set(log.eval.model for log in eval_logs), key=get_model_name),
            index=1,
            format_func=get_model_name,
            help="Name of the baseline model to compare against",
            label_visibility="visible",
            key="pairwise_analysis_baseline_name",
        )

    pairwise_logs = [
        log for log in eval_logs if log.eval.model in [model_name, baseline_name]
    ]

    if pairwise_logs:
        st.text("")  # Add a blank line for spacing
        pairwise_analysis_df = create_pairwise_analysis_table(
            pairwise_logs, model_name, baseline_name, default_values
        )

        if not pairwise_analysis_df.empty:
            st.dataframe(
                pairwise_analysis_df.style.apply(highlight_confidence_intervals, axis=1)
            )

            st.download_button(
                label="Download table as CSV",
                data=convert_df_to_csv(pairwise_analysis_df),
                file_name="pairwise_analysis.csv",
                mime="text/csv",
            )

            fig_pairwise = create_pairwise_scatter(pairwise_analysis_df)
            st.plotly_chart(fig_pairwise)
        else:
            st.warning(
                "These models have not been evaluated on overlapping tasks. No pairwise analysis data available. Select different models to see pairwise analysis.",
                icon="⚠️",
            )

    with st.expander("How is the pairwise analysis calculated?"):
        st.write(
            r"""
            Unpaired pairwise analysis (also known as naive or independent analysis) is a statistical method that compares two models without assuming any correlation between their responses to the same set of questions. This approach treats each model's accuracy as a separate, independent variable, leading to a more straightforward but potentially less precise evaluation.

            For each model, we extract:

            * Score ($S_A$, $S_B$): The performance measure assigned to each model.
            * Standard Error ($SE_A$, $SE_B$): The uncertainty in the score estimates.

            The difference in scores between the models is computed as:
            """
        )
        st.latex(r"\Delta S = S_A - S_B")

        st.write(
            """
            Since the models are assumed to be independent, the combined standard error (SE) is given by:
            """
        )
        st.latex(r"SE_{\text{unpaired}} = \sqrt{SE_A^2 + SE_B^2}")

        st.write(
            """
            Using this SE, we calculate the 95% Confidence Interval (CI) for the difference in scores:
            """
        )
        st.latex(
            r"CI = \left(\Delta - 1.96 \times SE_{\text{unpaired}}, \Delta + 1.96 \times SE_{\text{unpaired}}\right)"
        )

        st.write(
            """
            Z-score:
            """
        )
        st.latex(r"Z = \frac{\Delta S}{SE_{\text{unpaired}}}")

        st.write(
            """
            **Interpreting the Confidence Interval**
            """
        )
        st.markdown(r"""
            The confidence interval ($CI$) provides a range in which the true difference in scores is expected to lie with 95% certainty. The interpretation depends on whether the interval is entirely positive, entirely negative, or includes zero:
            * Entirely Positive ($CI > 0$): Model A significantly outperforms Model B, as the score difference is consistently positive.
            * Entirely Negative ($CI < 0$): Model B significantly outperforms Model A, as the score difference is consistently negative.
            * Includes Zero: There is no statistically significant difference between the two models, meaning that any observed score differences could be due to random variation rather than a meaningful performance gap.
            """)

        st.write(
            """
            **Implications of Unpaired Analysis**
            """
        )
        st.markdown(r"""
            * Wider Confidence Intervals: Since correlation is ignored, variance is higher, making the confidence intervals larger.
            * Less Statistical Power: The method does not leverage potential relationships between the two models' responses, leading to less precise conclusions.
            * Appropriate for Completely Independent Data: If the models were tested on different sets of questions, this would be the correct approach.
            """)

    st.markdown("""
                **Note:** this is an unpaired analysis, which compares only overall average scores between models without examining performance on individual questions. A more precise approach would be a paired-differences test, which examines how each model performs on identical questions. This method reveals true performance differences by accounting for varying question difficulty. Paired analysis helps distinguish whether one model is genuinely better or if differences are simply due to which questions were easier for each model. To conduct your own paired-differences test, refer to this [Colab notebook](https://colab.research.google.com/drive/1dgJEjbjuyYB1FlKQqN2d1wtYQbcE54OK?usp=sharing).
                """)

    st.divider()
    st.subheader("Download evaluation logs")
    st.markdown("""
                Select the evaluation task(s) and model name(s) you want to download. Clicking the button below will generate temporary links to the evaluation logs in the AWS S3 bucket that are valid for 1 hour. The zip file contains the [EvalLog object](https://inspect.aisi.org.uk/eval-logs.html) from Inspect AI in `.eval` binary format.
                """)

    col1, col2 = st.columns(2)

    with col1:
        tasks_to_download = st.multiselect(
            "Evaluation/task",
            sorted(set(log.eval.task for log in eval_logs)),
            default=[],
            format_func=lambda option: option.removeprefix("inspect_evals/"),
            help="Name of the evaluation and the task",
            label_visibility="visible",
            key="download_task_name",
        )

    task_filtered_logs_to_download: list[DashboardLog] = [
        log for log in eval_logs if log.eval.task in tasks_to_download
    ]

    with col2:
        models_to_download = st.multiselect(
            "Model names",
            sorted(
                set(log.eval.model for log in task_filtered_logs_to_download),
                key=get_model_name,
            ),
            default=[],
            format_func=get_model_name,
            help="Name of the model",
            label_visibility="visible",
            key="download_model_name",
        )

    model_filtered_logs_to_download: list[DashboardLog] = [
        log
        for log in task_filtered_logs_to_download
        if log.eval.model in models_to_download
    ]

    if st.button("Generate links to logs"):
        responses = []
        for log in model_filtered_logs_to_download:
            bucket_name, object_name = parse_s3_url_for_presigned_url(log.location)
            response = create_presigned_url(bucket_name, object_name, expiration=3600)
            if response:
                responses.append(
                    {
                        "Task name": log.eval.task.removeprefix("inspect_evals/"),
                        "Model name": log.model_metadata.name,
                        "Download link": f"[:material/download:]({response})",
                    }
                )

        st.table(pd.DataFrame(responses))


@st.cache_data
def convert_df_to_csv(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode("utf-8")


def get_model_name(path: str) -> str:
    """Extract the model name from a full path <provider_name>/<model_name>.

    Args:
        path: Full path containing <provider_name>/<model_name>

    Returns:
        The last part of the path after the last '/'

    """
    return path.split("/")[-1]
