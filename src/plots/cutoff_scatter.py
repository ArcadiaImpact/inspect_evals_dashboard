import pandas as pd
import plotly.graph_objs as go
import streamlit as st

from inspect_evals_dashboard_schema import DashboardLog

from src.log_utils.dashboard_log_utils import get_scorer_by_name
from src.plots.plot_utils import create_hover_text


@st.cache_data(hash_funcs={DashboardLog: id})
def create_cutoff_scatter(
    eval_logs: list[DashboardLog],
    scorer: str,
    metric: str,
) -> go.Figure:
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
    if eval_logs and getattr(eval_logs[0].task_metadata, 'human_baseline', None):
        human_baseline = eval_logs[0].task_metadata.human_baseline.score

    plot_data = []
    for log in eval_logs:
        scorer = get_scorer_by_name(log, scorer)
        metric_value = scorer.metrics[metric].value
        stderr = (
            scorer.metrics.get("stderr", 0).value
            if "stderr" in scorer.metrics
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

    color_palette = ["#74aa9c", "#8e44ad", "#e67e22", "#3498db", "#e74c3c", "#2ecc71", "#f1c40f", "#1abc9c", "#9b59b6", "#d35400"]
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

    # Create performance frontier by only keeping points that improve upon previous max
    frontier_points = []
    current_max = float('-inf')
    for _, row in best_performers.iterrows():
        if row['value'] > current_max:
            frontier_points.append(row)
            current_max = row['value']
    
    frontier_df = pd.DataFrame(frontier_points)
    
    if not frontier_df.empty:
        fig.add_trace(
            go.Scatter(
                x=frontier_df["date"],
                y=frontier_df["value"],
                mode="lines",
                name="Performance frontier",
                line=dict(color="rgba(100, 100, 100, 0.5)", width=2),
                hovertemplate="Mean: %{y:.2f}<br>%{customdata}<extra></extra>",
                customdata=frontier_df["hover_text"],
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
        # TODO:Consider setting yaxis_range between some min and max value (test with real data)
        # yaxis=dict(
        #     range=[0, max(df['value'].max() * 1.1, human_baseline or 0)],  # Add 10% padding to the max value
        #     zeroline=True,
        # ),
        xaxis_tickangle=45,
    )

    return fig
