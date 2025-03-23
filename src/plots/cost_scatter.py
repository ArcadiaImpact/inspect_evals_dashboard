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
def create_cost_scatter(
    eval_logs: list[DashboardLog],
    scorer_name: str,
    metric_name: str,
) -> go.Figure:
    """Create a plotly figure showing model performance vs. cost.

    Args:
        eval_logs (list[DashboardLog]): The logs to create the scatter plot from.
        scorer_name (str): The scorer to use for the metric (log.results.scores[].score.name).
        metric_name (str): The metric to use for the scatter plot.

    Returns:
        go.Figure: The plotly figure.

    """
    human_baseline = get_human_baseline(eval_logs[0])

    plot_data = []
    for log in eval_logs:
        scorer_obj = get_scorer_by_name(log, scorer_name)
        metric_value = scorer_obj.metrics[metric_name].value
        stderr = (
            scorer_obj.metrics["stderr"].value if "stderr" in scorer_obj.metrics else 0
        )

        # Get the cost estimate
        total_cost = (
            log.cost_estimates["total"] if hasattr(log, "cost_estimates") else None
        )

        if metric_value and total_cost is not None:
            plot_data.append(
                {
                    "model": log.model_metadata.name,
                    "provider": log.model_metadata.provider,
                    "value": metric_value,
                    "cost": total_cost,
                    "stderr": stderr,
                    "human_baseline": human_baseline,
                    "hover_text": create_hover_text(log, human_baseline),
                }
            )

    df = pd.DataFrame(plot_data)
    fig = go.Figure()

    providers = sorted(df["provider"].unique())  # Sort providers alphanumerically
    # Use a color palette for different providers
    color_palette = get_provider_color_palette(set(providers))

    # Add scatter points for each provider
    for provider_name in providers:
        provider_data = df[df["provider"] == provider_name]

        fig.add_trace(
            go.Scatter(
                x=provider_data["cost"],
                y=provider_data["value"],
                error_y=dict(type="data", array=provider_data["stderr"], visible=True),
                mode="markers",
                name=provider_name,
                marker=dict(size=10, color=color_palette.get(provider_name, "#666666")),
                hovertemplate="Score: %{y:.2f}<br>Cost: $%{x:.4f}<br>%{customdata}<extra></extra>",
                customdata=provider_data["hover_text"],
            )
        )

    # Add human baseline if it exists
    if human_baseline is not None:
        fig.add_trace(
            go.Scatter(
                x=[df["cost"].min(), df["cost"].max()],
                y=[human_baseline, human_baseline],
                mode="lines",
                line=dict(color="rgba(174, 198, 207, 1.0)", dash="dot", width=2),
                hovertemplate="",
                name="Human baseline",
            )
        )

    # Update layout
    fig.update_layout(
        title=f"Comparison of {metric_name} vs. estimated cost of running the evaluation",
        xaxis_title="Estimated cost (USD)",
        yaxis_title=f"Value of {metric_name} metric",
        xaxis=dict(
            tickformat="$,.2f"  # Format as currency
        ),
    )

    return fig
