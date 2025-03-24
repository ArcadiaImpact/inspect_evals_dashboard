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
    hover_text = create_hover_text(eval_logs[0])

    assert "Model:" in hover_text
    assert "Human baseline:" in hover_text
