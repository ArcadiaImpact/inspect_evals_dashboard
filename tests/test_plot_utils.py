from inspect_evals.metadata import HumanBaseline
from src.plots.plot_utils import (
    create_hover_text,
    get_human_baseline,
    get_provider_color_palette,
)


def test_human_baseline(eval_logs):
    log = eval_logs[0]
    assert get_human_baseline(log) is None
    setattr(
        log.task_metadata,
        "human_baseline",
        HumanBaseline(metric="whatever", score=42, source="http://example.com/"),
    )
    assert get_human_baseline(log) == 42


def test_get_provider_color_palette():
    providers = {"A", "B"}
    palette = get_provider_color_palette(providers)

    assert len(palette) == 2
    assert palette["A"].startswith("#")


def test_create_hover_text(eval_logs):
    assert create_hover_text(eval_logs[0]) == (
        "Model: test-model<br>"
        "Epochs: 1<br>"
        "Model provider: test-provider<br>"
        "Model family: test-model-family<br>"
        "Knowledge cutoff date: 2024-01-01<br>"
        "Release date: 2025-01-01<br>"
        "Training flops: Unknown<br>"
        "Accessibility: closed-source<br>"
        "Country of origin: USA<br>"
        "Context window size: 123<br>"
        "API provider: test-provider<br>"
        "API endpoint: test-model<br>"
        "Cost estimate: 0.0002 USD<br>"
        "Run timestamp: 2025-01-01T00:00:00+00:00<br>"
        "Human baseline: N/A<br>"
    )
