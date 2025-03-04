"""Temporarily copy from inspect_evals_scoring.process_log to avoid dependency on inspect_evals_scoring
which is a private repository. Streamlit Cloud doesn't support private Github dependencies.
"""
from datetime import date
from typing import Any

from inspect_ai.log import (
    EvalPlan,
    EvalResults,
    EvalSampleReductions,
    EvalSpec,
    EvalStats,
)
from inspect_evals.metadata import EvalMetadata, TaskMetadata
from pydantic import BaseModel, computed_field


class ModelMetadata(BaseModel):
    """Metadata about a model, including its capabilities and pricing"""

    name: str  # e.g., "gpt-4o"
    provider: str  # e.g., "OpenAI"
    family: str  # e.g., "gpt"
    release_date: date  # e.g., 2024-05-13
    knowledge_cutoff_date: date  # e.g., 2023-04-01
    training_flops: str | None  # e.g., "Unknown"
    api_provider: str  # e.g., "OpenAI"
    api_endpoint: str  # e.g., "gpt-4o-2024-11-20"
    api_input_mtok_price_usd: float  # e.g., 2.5
    api_cached_input_mtok_price_usd: float  # e.g., 1.25
    api_output_mtok_price_usd: float  # e.g., 10.0
    attributes: dict[str, str | int] = {}
    # Example values:
    """
    {
        "accessibility": "closed-source",
        "country_of_origin": "USA",
        "context_window_size_tokens": 128000
    }
    """


class DashboardLog(BaseModel):
    schema_version: str = "1.0"
    plan: EvalPlan
    results: EvalResults
    stats: EvalStats
    # error: EvalError  # ?
    # samples: list[EvalSample]
    reductions: list[EvalSampleReductions]
    location: str
    eval: EvalSpec
    eval_metadata: EvalMetadata
    task_metadata: TaskMetadata
    model_metadata: ModelMetadata

    @computed_field
    @property
    def cost_estimates(self) -> dict[str, Any]:
        per_model_estimates = {
            used_model: {
                "input_cost": usage.input_tokens
                * self.model_metadata.api_input_mtok_price_usd
                / 1_000_000.0,
                "output_cost": usage.output_tokens
                * self.model_metadata.api_output_mtok_price_usd
                / 1_000_000.0,
            }
            for used_model, usage in self.stats.model_usage.items()
        }
        total = sum(
            sum(model_estimate.values())
            for model_estimate in per_model_estimates.values()
        )
        return {
            "total": total,
            "per_model_estimates": per_model_estimates,
        }
