"""Load role tiers and enforce tool allowlists from YAML configuration."""
from pathlib import Path
from typing import Any

def load_roles(path: str | Path) -> dict[str,Any]:
    try: import yaml
    except ImportError as exc: raise RuntimeError("Install project base dependencies for YAML config support") from exc
    raw=yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    roles=raw.get("agents",{}); tiers={"fast","strong","deep"}
    for name,role in roles.items():
        if role.get("tier") not in tiers: raise ValueError(f"Agent {name} has an invalid model tier")
        if not isinstance(role.get("tools",[]),list): raise ValueError(f"Agent {name} tools must be a list")
    return roles

def assert_tool_allowed(roles: dict[str,Any], role_name: str, tool_name: str) -> None:
    if role_name not in roles: raise KeyError(f"Unknown agent role: {role_name}")
    if tool_name not in roles[role_name].get("tools",[]): raise PermissionError(f"Tool {tool_name} is not allowed for role {role_name}")
