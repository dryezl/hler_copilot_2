"""
HLER Lab - DataAgent
Stage: DATA_COLLECTION

Activates the relevant dataset for the selected research question.
Enforces dataset isolation: only one dataset may be active per run.
"""

from __future__ import annotations

import os
from pathlib import Path

from agents.base_agent import BaseAgent
from config.run_state import PipelineStage, RunState

PROCESSED_DIR = "data/processed"


class DataIsolationError(RuntimeError):
    """Raised when an agent attempts to switch datasets without human approval."""


class DataAgent(BaseAgent):
    """
    Activates the relevant dataset and enforces dataset isolation.

    Dataset isolation is a core HLER principle: cross-domain data mixing
    must never happen silently. Switching datasets within a run requires
    explicit human approval.
    """

    stage = PipelineStage.DATA_COLLECTION

    def run(self, state: RunState, dataset_name: str = "", **kwargs) -> RunState:
        self._assert_stage(state)
        self._log(state, "Starting data collection stage.")

        if not dataset_name:
            dataset_name = self._select_dataset(state)

        self._activate_dataset(state, dataset_name)
        state.advance_stage()
        return state

    # ------------------------------------------------------------------ #
    # Internal helpers                                                     #
    # ------------------------------------------------------------------ #

    def _activate_dataset(self, state: RunState, dataset_name: str) -> None:
        """
        Activate a dataset, enforcing isolation rules.

        Raises DataIsolationError if a different dataset is already active
        and the switch has not been approved via a human gate.
        """
        if (
            state.active_dataset
            and state.active_dataset != dataset_name
            and not state.is_gate_approved("GATE_DATASET_SWITCH")
        ):
            raise DataIsolationError(
                f"Cannot switch from dataset '{state.active_dataset}' to "
                f"'{dataset_name}' without human approval. "
                "Use --approve --gate GATE_DATASET_SWITCH first."
            )

        processed_path = Path(PROCESSED_DIR) / dataset_name
        raw_path = Path("data/raw") / dataset_name

        if not processed_path.exists() and not raw_path.exists():
            self._log(
                state,
                f"Dataset '{dataset_name}' not found locally. "
                "In production, this would trigger download/preparation.",
            )

        state.active_dataset = dataset_name
        self._log(state, f"Dataset activated: {dataset_name}")
        state.register_artifact("active_dataset", f"{PROCESSED_DIR}/{dataset_name}")

    def _select_dataset(self, state: RunState) -> str:
        """
        Infer the dataset from the selected research question.

        In production, this would use an LLM to map the question to a
        dataset. Here we use simple keyword matching.
        """
        question = (state.research_question or "").lower()

        if "wage" in question or "labor" in question or "employment" in question:
            return "labor_dataset"
        if "health" in question or "medical" in question:
            return "health_dataset"
        if "agricultural" in question or "crop" in question or "yield" in question:
            return "agricultural_dataset"
        if "savings" in question or "behavioral" in question or "nudge" in question:
            return "behavioral_dataset"
        if "genetic" in question or "polygenic" in question:
            return "genoeconomics_dataset"
        return "general_dataset"
