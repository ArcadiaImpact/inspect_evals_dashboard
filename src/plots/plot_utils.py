import pandas as pd
# from inspect_evals_scoring.process_log import DashboardLog
from src.log_utils.dashboard_log import DashboardLog


def create_hover_text(log: DashboardLog, human_baseline: float = None) -> str:
    return (
        f"Model: {log.model_metadata.name}<br>"
        f"Epochs: {log.eval.config.epochs}<br>"
        f"Model provider: {log.model_metadata.provider}<br>"
        f"Model family: {log.model_metadata.family}<br>"
        f"Knowledge cutoff date: {log.model_metadata.knowledge_cutoff_date}<br>"
        f"API provider: {log.model_metadata.api_provider}<br>"
        f"API endpoint: {log.model_metadata.api_endpoint}<br>"
        f"Inspect Logs: <a href='{log.location}'>Link to logs</a><br>"
        f"Cost estimate: {log.cost_estimates['total']:.4f} USD<br>"
        f"Run timestamp: {log.eval.created}<br>"
        f"Human baseline: {human_baseline if human_baseline else 'N/A'}<br>"
    )


def highlight_confidence_intervals(
    row: pd.Series, ci_column: str = "95% Conf. Interval"
) -> list[str]:
    """Highlight positive and negative confidence intervals in a dataframe row"""
    styles = [""] * len(row)
    ci_values = row[ci_column]
    ci_column_idx = row.index.get_loc(ci_column)

    if isinstance(ci_values, str):
        try:
            # Extract the two numbers from the string (format like "(6.17%, 93.83%)")
            lower, upper = [float(x.strip(" %")) for x in ci_values.strip("()").split(",")]
            if lower > 0 and upper > 0:
                styles[ci_column_idx] = "background-color: #98BC98"  # Light green
            elif lower < 0 and upper < 0:
                styles[ci_column_idx] = "background-color: #BC9898"  # Light red
        except:
            pass
    return styles
