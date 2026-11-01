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
    assert result['match_status']=='unique_configuration_consistent_with_observed_capacities'
    assert result['researched_Model_family']=='A'
    assert result['capacity_fields_confirmed'] == ['RAM_detected', 'Storage_detected']


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


def test_dataset_import_is_idempotent_and_preserves_fields(tmp_path: Path):
    store = SQLiteStore(tmp_path / "db.sqlite")
    rows = [{"Candidate_ID": "L001", "OCR_context": "Core i5 8GB", "OCR_price": "44990"}]
    assert store.upsert_dataset_records("candidates", rows, "Candidate_ID", "input.csv") == 1
    assert store.upsert_dataset_records("candidates", rows, "Candidate_ID", "input.csv") == 1
    assert store.count_dataset_records("candidates") == 1
    restored = store.list_dataset_records("candidates", "Core i5")[0]["record"]
    assert restored == rows[0]


def test_local_model_router_rejects_non_loopback_ollama_endpoint(monkeypatch):
    monkeypatch.setenv("OLLAMA_BASE_URL", "https://remote.example:11434")
    with pytest.raises(ModelNotConfigured):
        ModelRouter({"fast": "ollama_chat/qwen2.5:7b"}, allow_remote=False).select("fast")



def test_configuration_match_does_not_match_8gb_inside_18gb():
    candidate = {
        "Brand_detected": "HP",
        "Processor_detected": "Intel Core i3-1315U",
        "RAM_detected": "8 GB",
        "Storage_detected": "512 GB SSD",
    }
    configurations = [{
        "Brand": "HP",
        "Processor": "Intel Core i3-1315U",
        "Model_family": "HP 15",
        "RAM_seen": "18GB DDR4",
        "Storage_seen": "512GB SSD",
    }]

    result = match_configuration(candidate, configurations)

    assert result["match_status"] == "ocr_configuration_mismatch"
    assert result["match_confidence"] == "low"


def test_configuration_match_keeps_missing_research_capacity_ambiguous():
    candidate = {
        "Brand_detected": "Lenovo",
        "Processor_detected": "AMD Ryzen 5 7520U",
        "RAM_detected": "8 GB",
        "Storage_detected": "512 GB SSD",
    }
    configurations = [
        {
            "Brand": "Lenovo",
            "Processor": "AMD Ryzen 5 7520U",
            "Model_family": "IdeaPad A",
            "RAM_seen": "8GB",
            "Storage_seen": "",
        },
        {
            "Brand": "Lenovo",
            "Processor": "AMD Ryzen 5 7520U",
            "Model_family": "IdeaPad B",
            "RAM_seen": "8GB",
            "Storage_seen": "512GB SSD",
        },
    ]

    result = match_configuration(candidate, configurations)

    assert result["match_status"] == "ambiguous_multiple_configurations"


def test_model_router_rejects_remote_api_base_override_before_provider_call():
    router = ModelRouter(
        {"fast": "ollama_chat/qwen2.5:7b"},
        allow_remote=False,
    )

    with pytest.raises(ModelNotConfigured, match="api_base override"):
        router.complete([], tier="fast", api_base="https://api.example.com/v1")


def test_model_router_rejects_hosted_vllm_without_remote_opt_in():
    with pytest.raises(ModelNotConfigured):
        ModelRouter(
            {"fast": "hosted_vllm/provider/model"},
            allow_remote=False,
        ).select("fast")


def test_model_router_requires_explicit_loopback_for_non_ollama_backend(monkeypatch):
    router = ModelRouter({"fast": "vllm/local-model"}, allow_remote=False)
    with pytest.raises(ModelNotConfigured, match="VLLM_BASE_URL"):
        router.select("fast")

    monkeypatch.setenv("VLLM_BASE_URL", "http://127.0.0.2:8000/v1")
    assert router.select("fast") == "vllm/local-model"



def test_workflow_rejects_duplicate_step_names_before_creating_a_run(tmp_path: Path):
    store = SQLiteStore(tmp_path / "db.sqlite")
    engine = WorkflowEngine(store)

    with pytest.raises(ValueError, match="must be unique"):
        engine.run(
            "duplicate",
            {},
            [Step("same", lambda _: {"first": True}), Step("same", lambda _: {"second": True})],
            run_id="duplicate-run",
        )

    assert store.get_run("duplicate-run") is None


def test_workflow_rejects_changed_step_order_on_resume(tmp_path: Path):
    store = SQLiteStore(tmp_path / "db.sqlite")
    engine = WorkflowEngine(store)
    steps = [
        Step("first", lambda _: {"first": True}),
        Step("second", lambda _: {"second": True}),
    ]
    engine.run("ordered", {}, steps, run_id="ordered-run")

    with pytest.raises(ValueError, match="differs from the saved checkpoint plan"):
        engine.run("ordered", {}, list(reversed(steps)), run_id="ordered-run")


def test_workflow_rejects_legacy_checkpoints_without_a_saved_plan(tmp_path: Path):
    store = SQLiteStore(tmp_path / "db.sqlite")
    store.create_run("legacy-run", "legacy", {})
    store.save_step("legacy-run", "first", "completed", {}, {"done": True})

    with pytest.raises(ValueError, match="legacy checkpoints"):
        WorkflowEngine(store).run(
            "legacy",
            {},
            [Step("first", lambda _: {"done": True})],
            run_id="legacy-run",
        )



def test_multi_dataset_import_rolls_back_every_table_on_write_failure(
    tmp_path: Path,
):
    store = SQLiteStore(tmp_path / "db.sqlite")
    batches = [
        {
            "dataset": "first",
            "rows": [{"Candidate_ID": "S1-001", "title": "Acer"}],
            "key_field": "Candidate_ID",
            "source_file": "first.csv",
        },
        {
            "dataset": "second",
            "rows": [{"title": "Missing stable key"}],
            "key_field": "Candidate_ID",
            "source_file": "second.csv",
        },
    ]

    with pytest.raises(KeyError):
        store.import_dataset_batches(
            batches,
            sources=[{
                "uri": "https://manufacturer.example/spec",
                "title": "Manufacturer specification",
            }],
        )

    assert store.count_dataset_records("first") == 0
    assert store.count_dataset_records("second") == 0
    assert store.list_sources() == []



def test_resume_rejects_a_new_step_revision(tmp_path: Path):
    store = SQLiteStore(tmp_path / "db.sqlite")
    engine = WorkflowEngine(store)
    engine.run("revisioned", {}, [Step("enrich", lambda _: {"v": 1}, revision="1")], run_id="revision-run")
    with pytest.raises(ValueError, match="differs from the saved checkpoint plan"):
        engine.run("revisioned", {}, [Step("enrich", lambda _: {"v": 2}, revision="2")], run_id="revision-run")


def test_workflow_rejects_blank_step_revision(tmp_path: Path):
    store = SQLiteStore(tmp_path / "db.sqlite")
    with pytest.raises(ValueError, match="non-empty revision"):
        WorkflowEngine(store).run("blank", {}, [Step("enrich", lambda _: {}, revision=" ")], run_id="blank-run")
    assert store.get_run("blank-run") is None
