import pandas as pd
import plotly.graph_objs as go  # type: ignore
import streamlit as st
from inspect_evals_dashboard_schema import DashboardLog
from src.log_utils.dashboard_log_utils import get_scorer_by_name
from src.plots.plot_utils import (
    create_hover_text,
    get_human_baseline,
    get_provider_color_palette,
)


@st.cache_data(hash_funcs={DashboardLog: id})
def create_cutoff_scatter(
    eval_logs: list[DashboardLog],
    scorer_name: str,
    metric_name: str,
) -> go.Figure:
    """Create a plotly figure showing model performance over time.

    Args:
        eval_logs (list[DashboardLog]): List of model evaluation logs
        scorer_name (str): Scorer to use for metric (log.results.scores[].score.name)
        metric_name (str): Metric to plot

    Returns:
        go.Figure: Plotly figure object

    """
    human_baseline = get_human_baseline(eval_logs[0])

    plot_data = []
    for log in eval_logs:
        scorer = get_scorer_by_name(log, scorer_name)
        metric_value = scorer.metrics[metric_name].value
        stderr = scorer.metrics["stderr"].value if "stderr" in scorer.metrics else 0
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

    df = pd.DataFrame(plot_data)
    df = df.sort_values("date")
    fig = go.Figure()

    providers = sorted(df["provider"].unique())  # Sort providers alphanumerically
    # Use a color palette for different providers
    color_palette = get_provider_color_palette(set(providers))

    for provider_name in providers:
        provider_data = df[df["provider"] == provider_name]

        fig.add_trace(
            go.Scatter(
                x=provider_data["date"],
                y=provider_data["value"],
                error_y=dict(type="data", array=provider_data["stderr"], visible=True),
                mode="markers",
                name=provider_name,
                marker=dict(size=10, color=color_palette.get(provider_name, "#666666")),
                hovertemplate="Score: %{y:.2f}<br>Standard Error: %{error_y.array:.2f}<br>%{customdata}<extra></extra>",
                customdata=provider_data["hover_text"],
            )
        )

    # Add line connecting highest performing models
    # Group by date and find max value for each dateÒ
    best_performers = df.loc[df.groupby("date")["value"].idxmax()]
    best_performers = best_performers.sort_values("date")

    # Create performance frontier by only keeping points that improve upon previous max
    frontier_points = []
    current_max = float("-inf")
    for _, row in best_performers.iterrows():
        if row["value"] > current_max:
            frontier_points.append(row)
            current_max = row["value"]

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
        title=f"Comparison of {metric_name} values across models by knowledge cutoff date",
        xaxis_title="Knowledge cutoff date",
        yaxis_title=f"Value of {metric_name} metric",
        # TODO:Consider setting yaxis_range between some min and max value (test with real data)
        # yaxis=dict(
        #     range=[0, max(df['value'].max() * 1.1, human_baseline or 0)],  # Add 10% padding to the max value
        #     zeroline=True,
        # ),
        xaxis_tickangle=45,
    )

    return fig
