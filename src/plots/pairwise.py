import numpy as np
import pandas as pd
import plotly.graph_objects as go  # type: ignore
import streamlit as st
from inspect_evals_dashboard_schema import DashboardLog
from src.plots.plot_utils import get_metric_value_from_score


@st.cache_data(hash_funcs={DashboardLog: id})
def create_pairwise_analysis_table(
    eval_logs: list[DashboardLog],
    model_name: str,
    baseline_name: str,
    default_values: dict[str, dict[str, str]],
):
    rows = []

    task_groups: dict[str, list[DashboardLog]] = {}
    for log in eval_logs:
        task = log.eval.task
        if task not in task_groups:
            task_groups[task] = []
        task_groups[task].append(log)

    for task, logs in task_groups.items():
        model_log = next((log for log in logs if model_name == log.eval.model), None)
        baseline_log = next(
            (log for log in logs if baseline_name == log.eval.model), None
        )

        if model_log and baseline_log:
            # Get the default scorer and metric for this task
            task_defaults = default_values.get(task, {})
            scorer_name = task_defaults.get("default_scorer")
            metric_name = task_defaults.get("default_metric")

            if not scorer_name or not metric_name:
                continue

            # Find the correct score objects by scorer name
            model_score = next(
                (
                    score
                    for score in model_log.results.scores
                    if score.name == scorer_name
                ),
                None,
            )
            baseline_score = next(
                (
                    score
                    for score in baseline_log.results.scores
                    if score.name == scorer_name
                ),
                None,
            )

            if not model_score or not baseline_score:
                continue

            # Extract values using the specified metric name
            model_score_value = get_metric_value_from_score(model_score, metric_name)
            baseline_score_value = get_metric_value_from_score(
                baseline_score, metric_name
            )
            model_se = get_metric_value_from_score(model_score, "stderr")
            baseline_se = get_metric_value_from_score(baseline_score, "stderr")

            # Skip if either standard error is 0
            if model_se == 0 or baseline_se == 0:
                continue

            # Calculate difference
            diff = model_score_value - baseline_score_value

            # Using the formula: SE_unpaired = sqrt(SE_A^2 + SE_B^2)
            combined_se = np.sqrt(model_se**2 + baseline_se**2)

            # Calculate confidence interval and z-score using the appropriate SE
            ci_lower = diff - 1.96 * combined_se
            ci_upper = diff + 1.96 * combined_se
            z_score = diff / combined_se

            rows.append(
                {
                    "Task": task.removeprefix("inspect_evals/"),
                    "# Questions": model_log.results.completed_samples,
                    "Model": model_name,
                    "Baseline": baseline_name,
                    "Model - Baseline (SE)": f"{diff * 100:.2f}% ({combined_se * 100:.2f}%)",
                    "95% Conf. Interval": f"({ci_lower * 100:.2f}%, {ci_upper * 100:.2f}%)",
                    "z-score": f"{z_score:.2f}",
                }
            )

    return pd.DataFrame(rows)


@st.cache_data
def create_pairwise_scatter(pairwise_analysis_df: pd.DataFrame) -> go.Figure:
    # Extract data from the DataFrame
    tasks = pairwise_analysis_df["Task"].tolist()

    # Parse the Model - Baseline (SE) column to get differences and standard errors
    diffs_and_se = pairwise_analysis_df["Model - Baseline (SE)"].str.extract(
        r"([-\d.]+)% \(([-\d.]+)%\)"
    )
    score_differences = (
        diffs_and_se[0].astype(float) / 100
    )  # Convert from percentage to decimal

    # Parse the confidence interval column
    ci_bounds = pairwise_analysis_df["95% Conf. Interval"].str.extract(
        r"\(([-\d.]+)%, ([-\d.]+)%\)"
    )
    lower_bounds = (
        ci_bounds[0].astype(float) / 100
    )  # Convert from percentage to decimal
    upper_bounds = (
        ci_bounds[1].astype(float) / 100
    )  # Convert from percentage to decimal

    # Calculate error bar sizes (half the width of the confidence interval)
    errors = (upper_bounds - lower_bounds) / 2

    # Determine colors and significance categories
    colors = []
    categories = []
    for lower, upper, diff in zip(lower_bounds, upper_bounds, score_differences):
        if lower > 0 or upper < 0:
            if diff > 0:
                colors.append("green")
                categories.append("Significantly better")
            else:
                colors.append("red")
                categories.append("Significantly worse")
        else:
            colors.append("gray")
            categories.append("Not significant")

    # Create figure
    fig = go.Figure()

    # Add scatter plot with error bars
    for i, task in enumerate(tasks):
        fig.add_trace(
            go.Scatter(
                x=[task],
                y=[score_differences[i]],
                error_y=dict(type="data", array=[errors[i]], visible=True),
                mode="markers",
                marker=dict(size=12, color=colors[i]),
                name=categories[i],
                showlegend=categories[i]
                not in [
                    t.name for t in fig.data
                ],  # Only show legend for first occurrence of each category
            )
        )

    # Add a reference line at y=0
    fig.add_shape(
        type="line",
        x0=-0.5,
        x1=len(tasks) - 0.5,
        y0=0,
        y1=0,
        line=dict(color="#808080", dash="dash"),
    )

    # Layout configuration
    fig.update_layout(
        title="Score differences with 95% Confidence Intervals",
        xaxis_title="Task",
        yaxis_title="Score difference",
        showlegend=True,
        height=max(400, len(tasks) * 50),  # Dynamic height based on number of tasks
        xaxis=dict(tickangle=45),  # Angle task names for better readability
    )

    return fig
