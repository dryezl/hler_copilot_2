"""
HLER Lab - PaperAgent
Stage: WRITING

Generates a structured manuscript draft using the working paper template.
Pauses at GATE_MODEL_REVIEW for Human PI to confirm model specification
before the draft is written.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone

from agents.base_agent import BaseAgent
from config.run_state import PipelineStage, RunState

MANUSCRIPTS_DIR = "outputs/manuscripts"
TEMPLATE_PATH = "papers/templates/working_paper.md"


class PaperAgent(BaseAgent):
    """
    Generates a structured working paper draft.

    Human gate: GATE_MODEL_REVIEW
    The Human PI must confirm the model specification before the draft
    is written.
    """

    stage = PipelineStage.WRITING

    def run(self, state: RunState, **kwargs) -> RunState:
        self._assert_stage(state)
        self._log(state, "Starting manuscript drafting stage.")

        os.makedirs(MANUSCRIPTS_DIR, exist_ok=True)

        model_spec = self._summarize_model_spec(state)

        print("\n--- Model Specification Summary ---")
        print(model_spec)
        print()

        selection = state.await_human_gate(
            gate="GATE_MODEL_REVIEW",
            prompt=(
                "Please review the econometric model specification above.\n"
                "Enter 'proceed' to generate the draft, or describe revisions."
            ),
        )

        if selection.strip().lower() != "proceed":
            self._log(
                state,
                f"Model revision requested before drafting: {selection}",
            )
            state.metadata["model_revision"] = selection

        draft_path = self._write_draft(state)
        state.register_artifact("manuscript_draft", draft_path)
        self._log(state, f"Draft manuscript written to {draft_path}")
        state.advance_stage()
        return state

    # ------------------------------------------------------------------ #
    # Internal helpers                                                     #
    # ------------------------------------------------------------------ #

    def _summarize_model_spec(self, state: RunState) -> str:
        """Summarize the econometric model for human review."""
        gate = state.gates.get("GATE_IDENTIFICATION_APPROVAL")
        identification = (
            f"approved by {gate.approved_by} (selection: {gate.selection})"
            if gate
            else "(pending)"
        )
        return (
            f"Research Question : {state.research_question or '(not set)'}\n"
            f"Active Dataset    : {state.active_dataset or '(none)'}\n"
            f"Identification    : {identification}\n"
            "Main Model        : OLS with HC3 robust standard errors\n"
            "Key Tables        : summary_statistics, main_regression\n"
        )

    def _write_draft(self, state: RunState) -> str:
        """Populate the working paper template and write the draft."""
        paper_num = state.paper_number or 0
        paper_id = f"hler_wp_{paper_num:03d}"
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        template = self._load_template()
        draft = template.replace("{{PAPER_NUMBER}}", f"{paper_num:03d}")
        draft = draft.replace("{{PAPER_ID}}", paper_id)
        draft = draft.replace("{{DATE}}", date_str)
        draft = draft.replace(
            "{{RESEARCH_QUESTION}}",
            state.research_question or "(research question not set)",
        )
        draft = draft.replace(
            "{{DATASET}}",
            state.active_dataset or "(dataset not specified)",
        )
        draft = draft.replace("{{RUN_ID}}", state.run_id)

        draft_path = os.path.join(MANUSCRIPTS_DIR, f"{paper_id}_draft.md")
        with open(draft_path, "w", encoding="utf-8") as f:
            f.write(draft)
        return draft_path

    def _load_template(self) -> str:
        """Load the working paper template."""
        if os.path.exists(TEMPLATE_PATH):
            with open(TEMPLATE_PATH, encoding="utf-8") as f:
                return f.read()
        return self._default_template()

    def _default_template(self) -> str:
        return """# Human-in-the-Loop Economic Research Working Papers No. {{PAPER_NUMBER}}

**{{PAPER_ID}}**  
Date: {{DATE}}  
Run ID: {{RUN_ID}}

---

## Abstract

_[To be completed by PaperAgent and reviewed by Human PI]_

Research question: {{RESEARCH_QUESTION}}

---

## 1. Introduction

_[Draft introduction — to be reviewed and edited by Human PI]_

---

## 2. Data

Dataset: {{DATASET}}

_[Data description — to be completed]_

---

## 3. Methodology

_[Econometric methodology — see identification_memo.md]_

---

## 4. Results

_[Main results — see main_regression tables]_

---

## 5. Discussion

_[Discussion of findings]_

---

## 6. Conclusion

_[Conclusion]_

---

## References

_[References]_

---

*Human-in-the-Loop Economic Research Working Papers*  
*Execution may be automated. Judgment must remain human.*
"""
