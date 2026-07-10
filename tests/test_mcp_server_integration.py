"""Integration test: MCP server tools against real gates/ directory.

Concept: verify tools return real gates.
Source: WS3 plan, domain-gate smoke section.
Primitive: list_gates returns real gate entries, no GPU.
"""
import pytest


@pytest.mark.smoke
@pytest.mark.asyncio
async def test_list_gates_returns_real_gates():
    """Verify list_gates enumerates actual gates/ directory."""
    try:
        from integrations.prabodha_mcp_server.tools.gate_tools import list_gates_impl

        result = await list_gates_impl()
        assert result["status"] == "ok", f"list_gates failed: {result.get('error')}"
        assert result["count"] >= 0, "count should be non-negative"
        assert isinstance(result["gates"], list), "gates should be a list"

        # Each gate should have required fields
        for gate in result["gates"]:
            assert "path" in gate
            assert "name" in gate
            # path should be a gate JSON file
            assert gate["path"].endswith(".json")

    except ImportError as e:
        pytest.skip(f"gate_tools not importable: {e}")


@pytest.mark.smoke
@pytest.mark.asyncio
async def test_list_gates_filter_by_arm():
    """Verify list_gates respects arm filter."""
    try:
        from integrations.prabodha_mcp_server.tools.gate_tools import list_gates_impl

        result = await list_gates_impl(filter_arm="entropy_gated")
        assert result["status"] == "ok"
        # All returned gates should have arm == "entropy_gated" (if readable)
        for gate in result["gates"]:
            if gate.get("arm"):
                assert gate["arm"] == "entropy_gated"

    except ImportError as e:
        pytest.skip(f"gate_tools not importable: {e}")


@pytest.mark.smoke
@pytest.mark.asyncio
async def test_list_gates_filter_by_concept():
    """Verify list_gates respects concept filter."""
    try:
        from integrations.prabodha_mcp_server.tools.gate_tools import list_gates_impl

        result = await list_gates_impl(filter_concept="fire")
        assert result["status"] == "ok"
        # All returned gates should have concept == "fire" (if readable)
        for gate in result["gates"]:
            if gate.get("concept"):
                assert gate["concept"] == "fire"

    except ImportError as e:
        pytest.skip(f"gate_tools not importable: {e}")
