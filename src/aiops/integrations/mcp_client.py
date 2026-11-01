"""Minimal MCP stdio client. Servers remain disabled until explicitly enabled."""
from __future__ import annotations
import json, os
from pathlib import Path
from typing import Any
from aiops.config import load_environment

class MCPRegistry:
    def __init__(self, config_path: str | Path) -> None:
        load_environment()
        self.path=Path(config_path)
        self.config=json.loads(self.path.read_text(encoding="utf-8"))
        self.servers=self.config.get("mcpServers",{})

    def server_names(self) -> list[str]:
        return sorted(self.servers)

    @staticmethod
    def resolve_env(raw: dict[str,str] | None) -> dict[str,str] | None:
        if not raw: return None
        resolved={}
        for key,value in raw.items():
            if value.startswith("${") and value.endswith("}"):
                name=value[2:-1]
                secret=os.getenv(name)
                if secret is None: raise RuntimeError(f"Required environment variable {name} is not set")
                resolved[key]=secret
            else: resolved[key]=value
        return resolved

    async def call_tool(self, server_name: str, tool_name: str, arguments: dict[str,Any] | None = None) -> Any:
        if server_name not in self.servers: raise KeyError(f"Unknown MCP server: {server_name}")
        spec=self.servers[server_name]
        if not spec.get("enabled",False): raise PermissionError(f"MCP server '{server_name}' is disabled")
        try:
            from mcp import ClientSession, StdioServerParameters
            from mcp.client.stdio import stdio_client
        except ImportError as exc: raise RuntimeError("Install with pip install -e '.[mcp]'") from exc
        params=StdioServerParameters(command=spec["command"],args=spec.get("args",[]),env=self.resolve_env(spec.get("env")))
        async with stdio_client(params) as (read_stream,write_stream):
            async with ClientSession(read_stream,write_stream) as session:
                await session.initialize()
                available=await session.list_tools()
                if tool_name not in {item.name for item in available.tools}: raise KeyError(f"Unknown tool '{tool_name}' on server '{server_name}'")
                return await session.call_tool(tool_name,arguments or {})
