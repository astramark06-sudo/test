"""Deterministic sequential workflow runner with durable SQLite checkpoints."""
from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass
from typing import Any, Callable

from aiops.storage.sqlite import SQLiteStore


_PLAN_STEP_NAME = "__aiops_workflow_plan__"


@dataclass(frozen=True)
class Step:
    name: str
    handler: Callable[[dict[str, Any]], dict[str, Any]]
    revision: str = "1"


class WorkflowEngine:
    def __init__(self, store: SQLiteStore) -> None:
        self.store = store

    @staticmethod
    def _plan(workflow: str, steps: list[Step]) -> dict[str, Any]:
        if not isinstance(workflow, str) or not workflow.strip():
            raise ValueError("Workflow name must be a non-empty string")

        names = [step.name for step in steps]
        if any(not isinstance(name, str) or not name.strip() for name in names):
            raise ValueError("Every workflow step must have a non-empty name")
        if _PLAN_STEP_NAME in names:
            raise ValueError(f"Step name {_PLAN_STEP_NAME!r} is reserved")
        if len(names) != len(set(names)):
            raise ValueError("Workflow step names must be unique")
        if any(not callable(step.handler) for step in steps):
            raise TypeError("Every workflow step handler must be callable")
        if any(
            not isinstance(step.revision, str) or not step.revision.strip()
            for step in steps
        ):
            raise ValueError("Every workflow step must have a non-empty revision")

        definition = {
            "workflow": workflow,
            "step_names": names,
            "step_revisions": [step.revision for step in steps],
        }
        canonical = json.dumps(definition, sort_keys=True, separators=(",", ":"))
        return {**definition, "fingerprint": hashlib.sha256(canonical.encode()).hexdigest()}

    def run(
        self,
        workflow: str,
        payload: dict[str, Any],
        steps: list[Step],
        run_id: str | None = None,
        resume: bool = True,
    ) -> dict[str, Any]:
        plan = self._plan(workflow, steps)
        run_id = run_id or uuid.uuid4().hex
        existing = self.store.get_run(run_id)

        if existing and not resume:
            raise ValueError(f"Run {run_id} already exists; use a new run_id")
        if existing and (
            existing["workflow"] != workflow or existing["input"] != payload
        ):
            raise ValueError(
                "Existing run ID has a different workflow or input payload"
            )

        if not existing:
            self.store.create_run(run_id, workflow, payload)

        recorded_plan = self.store.get_step(run_id, _PLAN_STEP_NAME)
        if recorded_plan:
            if recorded_plan.get("output") != plan:
                raise ValueError(
                    "Workflow definition differs from the saved checkpoint plan; "
                    "use a new run_id instead of resuming stale step outputs"
                )
        else:
            # A pre-plan run may contain checkpoints but cannot prove which step
            # order produced them. Refuse an unsafe resume instead of guessing.
            prior_steps = self.store.list_steps(run_id)
            if prior_steps:
                raise ValueError(
                    "Existing run has legacy checkpoints without a workflow plan; "
                    "start a new run_id to avoid reusing stale outputs"
                )
            self.store.save_step(
                run_id,
                _PLAN_STEP_NAME,
                "completed",
                input_data=plan,
                output=plan,
            )

        state = dict(payload)
        state["run_id"] = run_id
        try:
            self.store.set_run_status(run_id, "running")
            for step in steps:
                checkpoint = self.store.get_step(run_id, step.name)
                if checkpoint and checkpoint["status"] == "completed":
                    if checkpoint["output"]:
                        state.update(checkpoint["output"])
                    continue

                self.store.save_step(run_id, step.name, "running", state)
                try:
                    result = step.handler(dict(state))
                    if not isinstance(result, dict):
                        raise TypeError(f"Step {step.name} must return a dict")
                    state.update(result)
                    self.store.save_step(
                        run_id, step.name, "completed", state, result
                    )
                except Exception as exc:
                    self.store.save_step(
                        run_id,
                        step.name,
                        "failed",
                        state,
                        error=f"{type(exc).__name__}: {exc}",
                    )
                    raise

            self.store.set_run_status(run_id, "completed", state)
            return state
        except Exception as exc:
            self.store.set_run_status(
                run_id, "failed", error=f"{type(exc).__name__}: {exc}"
            )
            raise
