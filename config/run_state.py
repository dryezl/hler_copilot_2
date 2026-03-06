"""
HLER Lab - RunState
Shared state object passed through the entire research pipeline.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


class PipelineStage(str, Enum):
    INIT = "INIT"
    DATA_AUDIT = "DATA_AUDIT"
    QUESTIONING = "QUESTIONING"
    DATA_COLLECTION = "DATA_COLLECTION"
    ANALYSIS = "ANALYSIS"
    WRITING = "WRITING"
    REVIEW = "REVIEW"
    FINAL_APPROVAL = "FINAL_APPROVAL"
    COMPLETE = "COMPLETE"


STAGE_ORDER = [
    PipelineStage.INIT,
    PipelineStage.DATA_AUDIT,
    PipelineStage.QUESTIONING,
    PipelineStage.DATA_COLLECTION,
    PipelineStage.ANALYSIS,
    PipelineStage.WRITING,
    PipelineStage.REVIEW,
    PipelineStage.FINAL_APPROVAL,
    PipelineStage.COMPLETE,
]


@dataclass
class GateRecord:
    """Record of a human gate approval."""
    gate: str
    approved_by: str
    approved_at: str
    selection: Any
    notes: str = ""


@dataclass
class AuditEntry:
    """Single entry in the pipeline audit log."""
    timestamp: str
    stage: str
    agent: str
    message: str


@dataclass
class RunState:
    """
    Shared state object for the HLER pipeline.

    Owns the current stage, active dataset lock, human gate records,
    and the full audit log. Passed through every agent and persisted
    to disk after each stage transition.
    """

    run_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    stage: PipelineStage = PipelineStage.INIT
    active_dataset: Optional[str] = None
    research_question: Optional[str] = None
    paper_number: Optional[int] = None

    gates: dict[str, GateRecord] = field(default_factory=dict)
    audit_log: list[AuditEntry] = field(default_factory=list)
    artifacts: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------ #
    # Logging                                                              #
    # ------------------------------------------------------------------ #

    def log(self, message: str, agent: str = "system") -> None:
        """Append an entry to the audit log."""
        entry = AuditEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            stage=self.stage.value,
            agent=agent,
            message=message,
        )
        self.audit_log.append(entry)
        print(f"[{entry.timestamp}] [{entry.stage}] [{entry.agent}] {message}")

    # ------------------------------------------------------------------ #
    # Stage transitions                                                    #
    # ------------------------------------------------------------------ #

    def advance_stage(self) -> None:
        """Move to the next pipeline stage."""
        idx = STAGE_ORDER.index(self.stage)
        if idx < len(STAGE_ORDER) - 1:
            next_stage = STAGE_ORDER[idx + 1]
            self.log(f"Stage transition: {self.stage.value} → {next_stage.value}")
            self.stage = next_stage
        else:
            self.log("Pipeline already at final stage.")

    # ------------------------------------------------------------------ #
    # Human gates                                                          #
    # ------------------------------------------------------------------ #

    def await_human_gate(
        self,
        gate: str,
        prompt: str,
        options: Optional[list] = None,
    ) -> Any:
        """
        Pause execution and request explicit human input.

        In interactive mode this reads from stdin. In CI/batch mode the
        gate must be pre-populated via ``record_gate_approval`` before
        this method is called.

        Returns the human's selection.
        """
        if gate in self.gates:
            record = self.gates[gate]
            self.log(
                f"Gate '{gate}' already approved by {record.approved_by} "
                f"at {record.approved_at}. Selection: {record.selection}",
                agent="gate_manager",
            )
            return record.selection

        print("\n" + "=" * 60)
        print(f"⏸  HUMAN GATE REQUIRED: {gate}")
        print("=" * 60)
        print(prompt)
        if options:
            for i, opt in enumerate(options, 1):
                print(f"  [{i}] {opt}")
        print()

        selection = input("Your input: ").strip()
        approver = input("Your name/identifier: ").strip()
        notes = input("Optional notes: ").strip()

        self.record_gate_approval(
            gate=gate,
            approved_by=approver,
            selection=selection,
            notes=notes,
        )
        return selection

    def record_gate_approval(
        self,
        gate: str,
        approved_by: str,
        selection: Any,
        notes: str = "",
    ) -> None:
        """Record a human gate approval (used for pre-approval in batch mode)."""
        record = GateRecord(
            gate=gate,
            approved_by=approved_by,
            approved_at=datetime.now(timezone.utc).isoformat(),
            selection=selection,
            notes=notes,
        )
        self.gates[gate] = record
        self.log(
            f"Gate '{gate}' approved by '{approved_by}'. Selection: {selection}",
            agent="gate_manager",
        )

    def is_gate_approved(self, gate: str) -> bool:
        """Return True if the given gate has been approved by a human."""
        return gate in self.gates

    # ------------------------------------------------------------------ #
    # Artifacts                                                            #
    # ------------------------------------------------------------------ #

    def register_artifact(self, name: str, path: str) -> None:
        """Register an output artifact (figure, table, manuscript)."""
        self.artifacts[name] = path
        self.log(f"Artifact registered: {name} → {path}")

    # ------------------------------------------------------------------ #
    # Serialization                                                        #
    # ------------------------------------------------------------------ #

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "stage": self.stage.value,
            "active_dataset": self.active_dataset,
            "research_question": self.research_question,
            "paper_number": self.paper_number,
            "gates": {
                k: vars(v) for k, v in self.gates.items()
            },
            "audit_log": [vars(e) for e in self.audit_log],
            "artifacts": self.artifacts,
            "metadata": self.metadata,
        }

    def save(self, path: str) -> None:
        """Persist RunState to a JSON file."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        self.log(f"RunState saved to {path}")

    @classmethod
    def load(cls, path: str) -> "RunState":
        """Load RunState from a JSON file."""
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        state = cls(
            run_id=data["run_id"],
            stage=PipelineStage(data["stage"]),
            active_dataset=data.get("active_dataset"),
            research_question=data.get("research_question"),
            paper_number=data.get("paper_number"),
            artifacts=data.get("artifacts", {}),
            metadata=data.get("metadata", {}),
        )
        state.gates = {
            k: GateRecord(**v) for k, v in data.get("gates", {}).items()
        }
        state.audit_log = [
            AuditEntry(**e) for e in data.get("audit_log", [])
        ]
        return state
