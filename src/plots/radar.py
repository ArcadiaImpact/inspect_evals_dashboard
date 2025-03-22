from typing import Dict, List, Tuple

import plotly.graph_objs as go
import streamlit as st

from inspect_evals_dashboard_schema import DashboardLog


def normalize_metric(value: float, min_val: float, max_val: float) -> float:
    """Normalize a metric value to the range [0, 1]"""
    if max_val == min_val:
        return 0.5  # Return middle value if all values are the same
    return (value - min_val) / (max_val - min_val)


def create_radar_hover_text(log: DashboardLog) -> str:
    """Create hover text for radar chart showing model-specific information."""
    return f"Model: {log.model_metadata.name}<br>Provider: {log.model_metadata.provider}"


def get_task_min_max(category_logs: List[DashboardLog]) -> Dict[str, Tuple[float, float]]:
    """Get min and max values for each task in a category across all models."""
    task_bounds = {}
    
    for log in category_logs:
        task_name = log.eval.task
        for score in log.results.scores:
            for metric_name, metric in score.metrics.items():
                if metric_name != "stderr":
                    if task_name not in task_bounds:
                        task_bounds[task_name] = (float('inf'), float('-inf'))
                    current_min, current_max = task_bounds[task_name]
                    task_bounds[task_name] = (
                        min(current_min, metric.value),
                        max(current_max, metric.value)
                    )
    
    return task_bounds


@st.cache_data(hash_funcs={DashboardLog: id})
def create_radar_chart(category_logs: dict[str, list[DashboardLog]], selected_model: str) -> go.Figure:
    """
    Create a radar chart showing model performance across different evaluation categories.
    Each task is normalized using all models' scores, then averaged for the selected model.
    
    Args:
        category_logs: Dictionary mapping category names to lists of DashboardLogs
        selected_model: Name of the model to show performance for
        
    Returns:
        go.Figure: Plotly figure object
    """
    categories = []
    values = []
    errors = []
    hover_texts = []
    
    for category, logs in category_logs.items():
        if not logs:
            continue
            
        # Get min/max for each task in this category
        task_bounds = get_task_min_max(logs)
        
        # Get selected model's logs
        model_logs = [log for log in logs if log.model_metadata.name == selected_model]
        if not model_logs:
            continue
            
        # Get model info from the first log
        model_info = create_radar_hover_text(model_logs[0])
        
        # Calculate normalized scores for each task
        normalized_scores = []
        normalized_errors = []
        
        for log in model_logs:
            task_name = log.eval.task
            if task_name in task_bounds:
                task_min, task_max = task_bounds[task_name]
                for score in log.results.scores:
                    for metric_name, metric in score.metrics.items():
                        if metric_name != "stderr":
                            normalized_value = normalize_metric(metric.value, task_min, task_max)
                            normalized_scores.append(normalized_value)
                            # Normalize error relative to task range
                            if task_max != task_min:
                                normalized_error = score.metrics.get("stderr", 0).value / (task_max - task_min)
                            else:
                                normalized_error = 0
                            normalized_errors.append(normalized_error)
        
        if normalized_scores:
            # Calculate category average
            avg_value = sum(normalized_scores) / len(normalized_scores)
            avg_error = sum(normalized_errors) / len(normalized_errors)
            
            categories.append(category.capitalize())
            values.append(avg_value)
            errors.append(avg_error)
            hover_texts.append(model_info)
    
    # Create the radar chart
    fig = go.Figure()
    
    # Add the main performance trace
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Model Performance',
        hovertemplate="Category: %{theta}<br>Normalized score: %{r:.2f} (±%{customdata:.2f})<br>%{text}<extra></extra>",
        customdata=errors,
        text=hover_texts,
        line=dict(color='rgb(31, 119, 180)'),
        fillcolor='rgba(31, 119, 180, 0.2)'
    ))
    
    # Add error bars as a separate trace
    fig.add_trace(go.Scatterpolar(
        r=[v + e for v, e in zip(values, errors)],
        theta=categories,
        mode='lines',
        line=dict(color='rgba(31, 119, 180, 0.3)', width=1),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=[v - e for v, e in zip(values, errors)],
        theta=categories,
        mode='lines',
        line=dict(color='rgba(31, 119, 180, 0.3)', width=1),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Update layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        showlegend=False,
        title=f"Model performance across evaluation categories",
        height=600,
    )
    
    return fig 