"""
HLER Lab - Orchestrator
Owns the RunState, dispatches pipeline stages, and manages human gates.
"""

from __future__ import annotations

import argparse
import os
import sys

import yaml

# Allow running from the repository root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.data_audit_agent import DataAuditAgent
from agents.data_agent import DataAgent
from agents.econometrics_agent import EconometricsAgent
from agents.paper_agent import PaperAgent
from agents.question_agent import QuestionAgent
from agents.reviewer_agent import ReviewerAgent
from config.run_state import PipelineStage, RunState

STATE_FILE = "run_state.json"


class Orchestrator:
    """
    HLER pipeline orchestrator.

    Owns the RunState, dispatches each stage to the appropriate agent,
    and enforces human gates. The pipeline cannot advance past a gate
    without explicit human input.
    """

    AGENT_MAP = {
        PipelineStage.DATA_AUDIT: DataAuditAgent,
        PipelineStage.QUESTIONING: QuestionAgent,
        PipelineStage.DATA_COLLECTION: DataAgent,
        PipelineStage.ANALYSIS: EconometricsAgent,
        PipelineStage.WRITING: PaperAgent,
        PipelineStage.REVIEW: ReviewerAgent,
    }

    def __init__(self, config_path: str = "config/pipeline_config.yaml") -> None:
        with open(config_path, encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

    # ------------------------------------------------------------------ #
    # Public commands                                                      #
    # ------------------------------------------------------------------ #

    def init(self) -> RunState:
        """Create a new RunState and persist it."""
        state = RunState()
        state.log("HLER pipeline initialized.", agent="orchestrator")
        state.advance_stage()  # INIT → DATA_AUDIT
        state.save(STATE_FILE)
        print(f"\n✅ New run initialized. ID: {state.run_id}")
        print(f"   State saved to: {STATE_FILE}")
        return state

    def run(self) -> None:
        """Advance the pipeline by one stage."""
        state = self._load_state()

        if state.stage == PipelineStage.COMPLETE:
            print("✅ Pipeline is complete.")
            return

        if state.stage == PipelineStage.FINAL_APPROVAL:
            self._handle_final_approval(state)
            return

        agent_cls = self.AGENT_MAP.get(state.stage)
        if agent_cls is None:
            print(f"⚠️  No agent registered for stage {state.stage.value}.")
            return

        agent = agent_cls()
        state = agent.run(state)
        state.save(STATE_FILE)

    def approve(self, gate: str, selection: str = "", approver: str = "") -> None:
        """Pre-approve a human gate (for batch/CI use)."""
        state = self._load_state()
        if not approver:
            approver = input("Your name/identifier: ").strip()
        if not selection:
            selection = input(f"Selection for gate '{gate}': ").strip()
        state.record_gate_approval(
            gate=gate,
            approved_by=approver,
            selection=selection,
        )
        state.save(STATE_FILE)
        print(f"✅ Gate '{gate}' approved.")

    def status(self) -> None:
        """Print the current pipeline status."""
        state = self._load_state()
        print("\n" + "=" * 50)
        print("  HLER Pipeline Status")
        print("=" * 50)
        print(f"  Run ID   : {state.run_id}")
        print(f"  Stage    : {state.stage.value}")
        print(f"  Dataset  : {state.active_dataset or '(none)'}")
        print(f"  Question : {state.research_question or '(none)'}")
        print(f"  Gates    : {list(state.gates.keys()) or '(none approved)'}")
        print(f"  Artifacts: {list(state.artifacts.keys()) or '(none)'}")
        print("=" * 50 + "\n")

    # ------------------------------------------------------------------ #
    # Internal helpers                                                     #
    # ------------------------------------------------------------------ #

    def _load_state(self) -> RunState:
        if not os.path.exists(STATE_FILE):
            print(f"❌ No state file found at '{STATE_FILE}'. Run --init first.")
            sys.exit(1)
        return RunState.load(STATE_FILE)

    def _handle_final_approval(self, state: RunState) -> None:
        gate = "GATE_PUBLICATION_APPROVAL"
        selection = state.await_human_gate(
            gate=gate,
            prompt=(
                "This is the final approval gate.\n"
                "Please review the complete manuscript and reviewer report.\n"
                "Enter 'approve' to authorize publication or 'revise' to "
                "return to an earlier stage."
            ),
        )
        if selection.strip().lower() == "approve":
            state.advance_stage()  # FINAL_APPROVAL → COMPLETE
            paper_num = state.paper_number or 0
            paper_id = f"hler_wp_{paper_num:03d}"
            print(f"\n🎉 Publication approved! Working paper: {paper_id}")
        else:
            print(f"\n🔄 Revision requested: '{selection}'")
        state.save(STATE_FILE)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="HLER Lab Pipeline Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python agents/orchestrator.py --init
  python agents/orchestrator.py --run
  python agents/orchestrator.py --approve --gate GATE_QUESTION_SELECTION
  python agents/orchestrator.py --status
        """,
    )
    parser.add_argument("--init", action="store_true", help="Initialize a new pipeline run")
    parser.add_argument("--run", action="store_true", help="Advance the pipeline one stage")
    parser.add_argument("--approve", action="store_true", help="Approve a human gate")
    parser.add_argument("--gate", type=str, help="Gate name (used with --approve)")
    parser.add_argument("--status", action="store_true", help="Show current pipeline status")
    parser.add_argument(
        "--config",
        type=str,
        default="config/pipeline_config.yaml",
        help="Path to pipeline config (default: config/pipeline_config.yaml)",
    )
    args = parser.parse_args()

    orch = Orchestrator(config_path=args.config)

    if args.init:
        orch.init()
    elif args.run:
        orch.run()
    elif args.approve:
        if not args.gate:
            parser.error("--approve requires --gate <GATE_NAME>")
        orch.approve(gate=args.gate)
    elif args.status:
        orch.status()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
