"""
HLER Lab - BaseAgent
Abstract base class for all HLER pipeline agents.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from config.run_state import PipelineStage, RunState


class BaseAgent(ABC):
    """
    Abstract base class for all HLER pipeline agents.

    Every agent must declare its ``stage`` and implement ``run``.
    Agents receive a ``RunState``, perform their work, and return
    an updated ``RunState``.
    """

    stage: PipelineStage

    @abstractmethod
    def run(self, state: RunState, **kwargs) -> RunState:
        """
        Execute this agent's task.

        Parameters
        ----------
        state:
            The shared pipeline state. Must be updated and returned.
        **kwargs:
            Agent-specific keyword arguments (e.g. config paths,
            dataset names).

        Returns
        -------
        RunState
            The updated state after this agent's work is complete.
        """

    # ------------------------------------------------------------------ #
    # Helpers available to all agents                                      #
    # ------------------------------------------------------------------ #

    def _assert_stage(self, state: RunState) -> None:
        """Raise if the RunState is not at the expected stage."""
        if state.stage != self.stage:
            raise RuntimeError(
                f"{self.__class__.__name__} expects stage {self.stage.value}, "
                f"but RunState is at {state.stage.value}."
            )

    def _log(self, state: RunState, message: str) -> None:
        """Log a message attributed to this agent."""
        state.log(message, agent=self.__class__.__name__)
