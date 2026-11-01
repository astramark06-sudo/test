"""Deterministic sequential workflow runner with durable SQLite checkpoints."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable
import uuid
from aiops.storage.sqlite import SQLiteStore

@dataclass(frozen=True)
class Step:
    name: str
    handler: Callable[[dict[str, Any]], dict[str, Any]]

class WorkflowEngine:
    def __init__(self, store: SQLiteStore) -> None: self.store = store
    def run(self, workflow: str, payload: dict[str, Any], steps: list[Step], run_id: str | None = None, resume: bool = True) -> dict[str, Any]:
        run_id = run_id or uuid.uuid4().hex
        existing = self.store.get_run(run_id)
        if existing and not resume: raise ValueError(f"Run {run_id} already exists; use a new run_id")
        if existing and (existing["workflow"] != workflow or existing["input"] != payload): raise ValueError("Existing run ID has a different workflow or input payload")
        if not existing: self.store.create_run(run_id,workflow,payload)
        state = dict(payload); state["run_id"] = run_id
        try:
            self.store.set_run_status(run_id,"running")
            for step in steps:
                checkpoint = self.store.get_step(run_id,step.name)
                if checkpoint and checkpoint["status"] == "completed":
                    if checkpoint["output"]: state.update(checkpoint["output"])
                    continue
                self.store.save_step(run_id,step.name,"running",state)
                try:
                    result = step.handler(dict(state))
                    if not isinstance(result,dict): raise TypeError(f"Step {step.name} must return a dict")
                    state.update(result); self.store.save_step(run_id,step.name,"completed",state,result)
                except Exception as exc:
                    self.store.save_step(run_id,step.name,"failed",state,error=f"{type(exc).__name__}: {exc}")
                    raise
            self.store.set_run_status(run_id,"completed",state)
            return state
        except Exception as exc:
            self.store.set_run_status(run_id,"failed",error=f"{type(exc).__name__}: {exc}")
            raise
