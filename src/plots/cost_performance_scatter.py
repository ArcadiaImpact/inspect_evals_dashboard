import pandas as pd
import plotly.graph_objs as go
import streamlit as st

from inspect_evals_dashboard_schema import DashboardLog

from src.log_utils.dashboard_log_utils import get_scorer_by_name
from src.plots.plot_utils import create_hover_text

@st.cache_data(hash_funcs={DashboardLog: id})
def create_cost_performance_scatter(
    eval_logs: list[DashboardLog],
    scorer: str,
    metric: str,
) -> go.Figure:
    """
    Create a plotly figure showing model performance vs. cost.
    """
    # Get human baseline if available
    human_baseline = None
    if eval_logs and getattr(eval_logs[0].task_metadata, 'human_baseline', None):
        human_baseline = eval_logs[0].task_metadata.human_baseline.score

    plot_data = []
    for log in eval_logs:
        scorer_obj = get_scorer_by_name(log, scorer)
        metric_value = scorer_obj.metrics[metric].value
        stderr = scorer_obj.metrics.get("stderr", 0).value if "stderr" in scorer_obj.metrics else 0
        
        # Get the cost estimate
        total_cost = log.cost_estimates["total"] if hasattr(log, 'cost_estimates') else None
        
        if metric_value and total_cost is not None:
            plot_data.append({
                "model": log.model_metadata.name,
                "provider": log.model_metadata.provider,
                "value": metric_value,
                "cost": total_cost,
                "stderr": stderr,
                "human_baseline": human_baseline,
                "hover_text": create_hover_text(log, human_baseline),
            })

    # Convert to pandas DataFrame
    df = pd.DataFrame(plot_data)

    fig = go.Figure()

    # Use a color palette for different providers
    color_palette = ["#74aa9c", "#8e44ad", "#e67e22", "#3498db", "#e74c3c", "#2ecc71", "#f1c40f"]
    providers = df["provider"].unique()
    colors = {
        provider: color_palette[i % len(color_palette)] for i, provider in enumerate(providers)
    }

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
                marker=dict(size=10, color=colors.get(provider_name, "#666666")),
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
        title=f"Model {metric} vs. Estimated Cost",
        xaxis_title="Estimated Cost (USD)",
        yaxis_title=f"{metric.capitalize()} score",
        xaxis=dict(
            tickformat="$,.4f"  # Format as currency
        ),
        legend_title="Provider"
    )

    return fig