# from inspect_evals_scoring.process_log import DashboardLog
from inspect_evals_dashboard_schema import DashboardLog
from config import EvaluationConfig
from src.log_utils.dashboard_log_utils import dashboard_log_hash_func, find_metrics
from src.plots.plot_utils import create_hover_text
import pandas as pd
import plotly.graph_objs as go
import streamlit as st


@st.cache_data(hash_funcs={DashboardLog: dashboard_log_hash_func, EvaluationConfig: id})
def create_cutoff_scatter(
    eval_logs: list[DashboardLog],
    eval_configs: list[EvaluationConfig],
    metric: str,
):
    """
    Create a plotly figure showing model performance over time.

    Args:
        eval_logs (list[DashboardLog]): List of model evaluation logs
        metric (str): Metric to plot

    Returns:
        go.Figure: Plotly figure object
    """
    # Get human baseline if available, otherwise set to None
    human_baseline = None
    if eval_logs and eval_logs[0].task_metadata.baselines:
        human_baseline = next(
            (b.score for b in eval_logs[0].task_metadata.baselines if b.metric == metric),
            None,
        )

    plot_data = []
    for log in eval_logs:
        metrics = find_metrics(log, eval_configs)
        metric_value = metrics[metric].value
        stderr = (
            metrics.get("stderr", 0).value
            if "stderr" in metrics
            else 0
        )
        if metric_value:
            plot_data.append(
                {
                    "date": log.model_metadata.knowledge_cutoff_date,
                    "model": log.model_metadata.name,
                    "provider": log.model_metadata.provider,
                    "value": metric_value,
                    "stderr": stderr,
                    "human_baseline": human_baseline,
                    "hover_text": create_hover_text(log, human_baseline),
                }
            )

    # Convert to pandas DataFrame for easier manipulation
    df = pd.DataFrame(plot_data)
    df = df.sort_values("date")

    fig = go.Figure()

    color_palette = ["#74aa9c", "#8e44ad", "#e67e22", "#3498db", "#e74c3c", "#2ecc71", "#f1c40f"]
    providers = df["provider"].unique()
    colors = {
        provider: color_palette[i % len(color_palette)] for i, provider in enumerate(providers)
    }

    for provider_name in providers:
        provider_data = df[df["provider"] == provider_name]

        fig.add_trace(
            go.Scatter(
                x=provider_data["date"],
                y=provider_data["value"],
                error_y=dict(type="data", array=provider_data["stderr"], visible=True),
                mode="markers",
                name=provider_name,
                marker=dict(size=10, color=colors.get(provider_name, "#666666")),
                hovertemplate="Score: %{y:.2f}<br>Standard Error: %{error_y.array:.2f}<br>%{customdata}<extra></extra>",
                customdata=provider_data["hover_text"],
            )
        )

    # Add line connecting highest performing models
    # Group by date and find max value for each date
    best_performers = df.loc[df.groupby("date")["value"].idxmax()]
    best_performers = best_performers.sort_values("date")

    fig.add_trace(
        go.Scatter(
            x=best_performers["date"],
            y=best_performers["value"],
            mode="lines",
            name="Performance frontier",
            line=dict(color="rgba(100, 100, 100, 0.5)", width=2),
            hovertemplate="Mean: %{y:.2f}<br>%{customdata}<extra></extra>",
            customdata=provider_data["hover_text"],
        )
    )

    # Add human baseline if it exists
    if human_baseline is not None:
        fig.add_trace(
            go.Scatter(
                x=[df["date"].iloc[0], df["date"].iloc[-1]],
                y=[human_baseline, human_baseline],
                mode="lines",
                line=dict(color="rgba(174, 198, 207, 1.0)", dash="dot", width=2),
                hovertemplate="",
                name="Human baseline",
            )
        )

    # Update layout
    fig.update_layout(
        title=f"Comparison of {metric} values across models by knowledge cutoff date",
        xaxis_title="Knowledge cutoff date",
        yaxis_title=f"Value of {metric} metric",
        # TODO: Consider setting yaxis_range between some min and max value
        # yaxis_range=[0, 1],
        xaxis_tickangle=45,
    )

    return fig
