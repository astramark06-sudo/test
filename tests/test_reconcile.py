from aiops.validation.reconcile import reconcile_text


def test_matching_engine_outputs_produce_consensus():
    result = reconcile_text({
        "engine_a": [{"text": "Dell Latitude 5420"}],
        "engine_b": [{"text": "dell   latitude 5420"}],
    })
    assert result["consensus_text"] == "Dell Latitude 5420"
    assert result["conflict"] is False
    assert result["review_required"] is False


def test_conflicting_engine_outputs_are_preserved_and_flagged():
    result = reconcile_text({
        "engine_a": [{"text": "Dell Latitude 5420"}],
        "engine_b": [{"text": "Dell Latitude 5430"}],
    })
    assert result["consensus_text"] is None
    assert result["conflict"] is True
    assert result["review_required"] is True
    assert len(result["engine_readings"]) == 2


def test_empty_outputs_require_review():
    result = reconcile_text({"engine_a": []})
    assert result["review_required"] is True
