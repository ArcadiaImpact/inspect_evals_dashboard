from operator import itemgetter

import plotly.graph_objs as go  # type: ignore
import streamlit as st
from inspect_evals_dashboard_schema import DashboardLog
from src.log_utils.dashboard_log_utils import get_scorer_by_name
from src.plots.plot_utils import create_hover_text, get_human_baseline


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
            (
                v.value
                for k, v in get_scorer_by_name(log, scorer).metrics.items()
                if k == "stderr"
            ),
            0,  # Default to 0 if stderr metric is not found
        )
        for log in eval_logs
    ]

    # Zip and sort models, metric_values, metric_errors together by the value in metric_values (in reverse order)
    # Then unpack them back in 3 separate lists
    models, metric_values, metric_errors = zip(
        *sorted(
            zip(models, metric_values, metric_errors), key=itemgetter(1), reverse=True
        )
    )

    human_baseline = get_human_baseline(eval_logs[0])

    # Create hover text with detailed information
    hover_texts = []
    for log in eval_logs:
        hover_text = create_hover_text(log, human_baseline)
        hover_texts.append(hover_text)

    # Hide error bars if all errors are 0
    show_error_bars = any(error != 0 for error in metric_errors)

    hovertemplate = (
        "Score: %{y:.2f}<br>"
        + (
            "Standard Error: %{error_y.array:.4f}<br>"
            if show_error_bars
            else "Standard Error: N/A<br>"
        )
        + "%{customdata}<extra></extra>"
    )

    fig = go.Figure(
        data=[
            go.Bar(
                x=models,
                y=metric_values,
                error_y=dict(type="data", array=metric_errors, visible=show_error_bars),
                name=f"{metric} metric",
                marker_color="rgba(54, 122, 179, 0.85)",
                hovertemplate=hovertemplate,
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
