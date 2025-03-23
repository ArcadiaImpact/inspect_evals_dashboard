import pandas as pd
from inspect_evals_dashboard_schema import DashboardLog


def create_hover_text(log: DashboardLog, human_baseline: float | None = None) -> str:
    return (
        f"Model: {log.model_metadata.name}<br>"
        f"Epochs: {log.eval.config.epochs}<br>"
        f"Model provider: {log.model_metadata.provider}<br>"
        f"Model family: {log.model_metadata.family}<br>"
        f"Knowledge cutoff date: {log.model_metadata.knowledge_cutoff_date}<br>"
        f"Release date: {log.model_metadata.release_date}<br>"
        f"Training flops: {log.model_metadata.training_flops}<br>"
        f"Accessibility: {log.model_metadata.attributes['accessibility']}<br>"
        f"Country of origin: {log.model_metadata.attributes['country_of_origin']}<br>"
        f"Context window size: {log.model_metadata.attributes['context_window_size_tokens']}<br>"
        f"API provider: {log.model_metadata.api_provider}<br>"
        f"API endpoint: {log.model_metadata.api_endpoint}<br>"
        f"Cost estimate: {log.cost_estimates['total']:.4f} USD<br>"
        f"Run timestamp: {log.eval.created}<br>"
        f"Human baseline: {human_baseline if human_baseline else 'N/A'}<br>"
    )


def highlight_confidence_intervals(
    row: pd.Series, ci_column: str = "95% Conf. Interval"
) -> list[str]:
    """Highlight positive and negative confidence intervals in a dataframe row.

    Args:
        row (pd.Series): The row to highlight.
        ci_column (str): The column to highlight.

    Returns:
        list[str]: The styles for the row.

    """
    styles = [""] * len(row)
    ci_values = row[ci_column]
    ci_column_idx = row.index.get_loc(ci_column)

    if isinstance(ci_values, str):
        try:
            # Extract the two numbers from the string (format like "(6.17%, 93.83%)")
            lower, upper = [
                float(x.strip(" %")) for x in ci_values.strip("()").split(",")
            ]
            if lower > 0 and upper > 0:
                styles[ci_column_idx] = "background-color: #98BC98"  # Light green
            elif lower < 0 and upper < 0:
                styles[ci_column_idx] = "background-color: #BC9898"  # Light red
        except Exception:
            pass
    return styles


def get_human_baseline(log: DashboardLog) -> float | None:
    """Get the human baseline from the logs.

    Args:
        log (DashboardLog): The log to get the human baseline from.

    Returns:
        float | None: The human baseline.

    """
    human_baseline = getattr(log.task_metadata, "human_baseline", None)
    if human_baseline:
        return human_baseline.score
    return None


def get_provider_color_palette(providers: set[str]) -> dict[str, str]:
    """Get a color palette for providers.

    Args:
        providers (set[str]): The providers to get the color palette for.

    Returns:
        dict[str, str]: The color palette for the providers.

    """
    color_palette = [
        "#74aa9c",
        "#8e44ad",
        "#e67e22",
        "#3498db",
        "#e74c3c",
        "#2ecc71",
        "#f1c40f",
        "#1abc9c",
        "#9b59b6",
        "#d35400",
    ]
    return {
        provider: color_palette[i % len(color_palette)]
        for i, provider in enumerate(sorted(providers))
    }
