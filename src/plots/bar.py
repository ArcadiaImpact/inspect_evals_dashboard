import plotly.graph_objs as go  # type: ignore
import streamlit as st
from inspect_evals_dashboard_schema import DashboardLog
from src.log_utils.dashboard_log_utils import get_scorer_by_name
from src.plots.plot_utils import create_hover_text


@st.cache_data(hash_funcs={DashboardLog: id})
def create_bar_chart(
    eval_logs: list[DashboardLog], scorer: str, metric: str
) -> go.Figure:
    # Extract data from filtered logs
    models = [log.model_metadata.name for log in eval_logs]

    metric_values = [
        next(
            v.value
            for k, v in get_scorer_by_name(log, scorer).metrics.items()
            if k == metric
        )
        for log in eval_logs
    ]
    metric_errors = [
        next(
            v.value
            for k, v in get_scorer_by_name(log, scorer).metrics.items()
            if k == "stderr"
        )
        for log in eval_logs
    ]

    # Get human baseline if available, otherwise set to None
    human_baseline = getattr(eval_logs[0].task_metadata, "human_baseline", None)
    if eval_logs and human_baseline:
        human_baseline = human_baseline.score

    # TODO: Inspect logs link should be clickable
    hover_texts = []
    for log in eval_logs:
        hover_text = create_hover_text(log, human_baseline)
        hover_texts.append(hover_text)

    fig = go.Figure(
        data=[
            go.Bar(
                x=models,
                y=metric_values,
                error_y=dict(type="data", array=metric_errors, visible=True),
                name=f"{metric} metric",
                marker_color="rgba(54, 122, 179, 0.85)",
                # TODO: Handle missing standard error value
                hovertemplate="Score: %{y:.2f}<br>Standard Error: %{error_y.array:.2f}<br>%{customdata}<extra></extra>",
                customdata=hover_texts,
            )
        ]
    )

    if human_baseline is not None:
        fig.add_trace(
            go.Scatter(
                x=[models[0], models[-1]] if models else [],
                y=[human_baseline, human_baseline],
                name="Human baseline",
                hovertemplate="Human baseline: %{y:.2f}",
                mode="lines",
                line=dict(color="rgba(150, 123, 182, 1.0)", dash="dot", width=2),
            )
        )

    fig.update_layout(
        title=f"Comparison of {metric} values across models",
        xaxis_title="Models",
        yaxis_title=f"Value of {metric} metric",
    )

    return fig
