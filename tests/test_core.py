import json
from pathlib import Path
import pytest
from aiops.export.jsonl import write_jsonl
from aiops.integrations.mcp_client import MCPRegistry
from aiops.memory.store import MemoryStore
from aiops.research.matching import match_configuration
from aiops.runtime.model_router import ModelNotConfigured, ModelRouter
from aiops.storage.sqlite import SQLiteStore
from aiops.workflows.engine import Step, WorkflowEngine


def test_jsonl_has_one_record_per_line(tmp_path: Path):
    path=write_jsonl([{"x":1},{"y":"z"}],tmp_path/'records.jsonl')
    lines=path.read_text(encoding='utf-8').splitlines()
    assert len(lines)==2 and [json.loads(x) for x in lines]==[{"x":1},{"y":"z"}]


def test_workflow_checkpoints_and_resumes(tmp_path: Path):
    store=SQLiteStore(tmp_path/'db.sqlite'); engine=WorkflowEngine(store); calls={"a":0,"b":0}
    def a(state): calls["a"]+=1; return {"x":state["seed"]+1}
    def b(state): calls["b"]+=1; return {"y":state["x"]*2}
    first=engine.run('calc',{"seed":2},[Step('a',a),Step('b',b)],run_id='r1')
    second=engine.run('calc',{"seed":2},[Step('a',a),Step('b',b)],run_id='r1')
    assert first['y']==second['y']==6 and calls=={"a":1,"b":1}
    assert store.get_run('r1')['status']=='completed'


def test_failed_step_can_resume_with_same_input(tmp_path: Path):
    store=SQLiteStore(tmp_path/'db.sqlite'); engine=WorkflowEngine(store)
    with pytest.raises(ValueError): engine.run('wf',{},[Step('fail',lambda _: (_ for _ in ()).throw(ValueError('x')))],run_id='r2')
    result=engine.run('wf',{},[Step('fail',lambda _: {"done":True})],run_id='r2')
    assert result['done'] is True


def test_memory_search_namespaced(tmp_path: Path):
    memory=MemoryStore(SQLiteStore(tmp_path/'db.sqlite'))
    memory.remember('Laptop project','Preserve OCR prices separate from researched prices','laptops')
    assert len(memory.retrieve('OCR prices','laptops'))==1
    assert memory.retrieve('OCR prices','other')==[]


def test_router_blocks_remote_or_unconfigured_models():
    with pytest.raises(ModelNotConfigured): ModelRouter({"fast":"openai/model"},allow_remote=False).select('fast')
    with pytest.raises(ModelNotConfigured): ModelRouter({}).select('deep')


def test_configuration_match_requires_variant_disambiguation():
    candidate={"Brand_detected":"Acer","Processor_detected":"Intel Core i3-1315U","RAM_detected":"8 GB","Storage_detected":"512 GB SSD"}
    configs=[
        {"Brand":"Acer","Processor":"Intel Core i3-1315U","Model_family":"A","RAM_seen":"8GB","Storage_seen":"512GB SSD"},
        {"Brand":"Acer","Processor":"Intel Core i3-1315U","Model_family":"B","RAM_seen":"16GB","Storage_seen":"512GB SSD"}]
    result=match_configuration(candidate,configs)
    assert result['match_status']=='exact_configuration' and result['researched_Model_family']=='A'


def test_mcp_is_disabled_by_default(tmp_path: Path):
    path=tmp_path/'mcp.json'; path.write_text(json.dumps({"mcpServers":{"test":{"enabled":False}}}))
    registry=MCPRegistry(path)
    assert registry.server_names()==['test']
    with pytest.raises(PermissionError):
        import asyncio
        asyncio.run(registry.call_tool('test','ignored'))


def test_model_router_allows_only_known_local_ids_without_opt_in():
    assert ModelRouter({"fast": "ollama_chat/qwen2.5:7b"}, allow_remote=False).select("fast")
    with pytest.raises(ModelNotConfigured):
        ModelRouter({"fast": "gpt-4o"}, allow_remote=False).select("fast")


def test_usage_summary_aggregates_tokens(tmp_path: Path):
    store = SQLiteStore(tmp_path / "db.sqlite")
    store.record_model_usage("local-fast", "fast", 10, 4, 14, None, "run-1")
    store.record_model_usage("local-fast", "fast", 5, 3, 8, None, "run-1")
    summary = store.usage_summary("run-1")
    assert summary[0]["calls"] == 2
    assert summary[0]["total_tokens"] == 22
