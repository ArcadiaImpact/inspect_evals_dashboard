# from inspect_evals_scoring.process_log import DashboardLog
from src.log_utils.dashboard_log import DashboardLog
import plotly.graph_objs as go
import streamlit as st
from src.log_utils.dashboard_log_utils import dashboard_log_hash_func 
from src.plots.plot_utils import create_hover_text


@st.cache_data(hash_funcs={DashboardLog: dashboard_log_hash_func})
def create_bar_chart(eval_logs: list[DashboardLog], metric: str):
    # Extract data from filtered logs
    models = [log.model_metadata.name for log in eval_logs]

    # Find metrics by name (only one score per model)
    # TODO: Handle multiple scores per model
    metric_values = [
        next(v.value for k, v in log.results.scores[0].metrics.items() if k == metric)
        for log in eval_logs
    ]
    metric_errors = [
        next(v.value for k, v in log.results.scores[0].metrics.items() if k == "stderr")
        for log in eval_logs
    ]

    # Baseline value (using first model's baseline)
    human_baseline = None
    if eval_logs and eval_logs[0].task_metadata.baselines:
        human_baseline = next(
            (b.score for b in eval_logs[0].task_metadata.baselines if b.metric == metric),
            None,
        )

    # Create hover text with detailed information
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
                # TODO: Update hovertemplate - show metric name instead of "Mean"
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
        title=f"Comparison of {metric} values across models on {eval_logs[0].task_metadata.name}",
        xaxis_title="Models",
        yaxis_title=f"Value of {metric} metric"
    )

    return fig
