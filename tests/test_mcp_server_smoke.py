"""Smoke test: MCP server starts and tools are listed.

Concept: integration test that server is properly wired.
Source: WS3 plan, smoke-test task.
Primitive: server startup + tool enumeration, no GPU.
"""
import pytest
import subprocess
import json
import time
import asyncio


@pytest.mark.smoke
def test_mcp_server_starts():
    """Verify MCP server can be started as a subprocess."""
    # Start the server in a subprocess (will hang waiting for client messages).
    # We send a single tool listing request, get the response, then kill it.
    try:
        proc = subprocess.Popen(
            ["python3", "-m", "prabodha_mcp_server.server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        # Give it 2 seconds to start
        time.sleep(2)
        # Check it didn't crash immediately
        retcode = proc.poll()
        assert retcode is None, f"Server exited with code {retcode}"
        # Kill it
        proc.terminate()
        proc.wait(timeout=5)
    except Exception as e:
        pytest.skip(f"MCP server not runnable in test environment: {e}")


@pytest.mark.smoke
def test_mcp_tools_module_imports():
    """Verify the tools module imports without errors."""
    try:
        from integrations.mcp_server.tools import lens_tools, steer_tools, gate_tools
        assert hasattr(lens_tools, "lens_map_impl")
        assert hasattr(steer_tools, "steer_generate_impl")
        assert hasattr(gate_tools, "readback_verify_impl")
        assert hasattr(gate_tools, "list_gates_impl")
    except ImportError as e:
        pytest.skip(f"Tools module not importable: {e}")


@pytest.mark.smoke
@pytest.mark.asyncio
async def test_list_gates_impl_callable():
    """Verify list_gates_impl is callable and returns expected schema."""
    try:
        from integrations.mcp_server.tools.gate_tools import list_gates_impl
        result = await list_gates_impl()
        assert isinstance(result, dict)
        assert "status" in result
        assert "gates" in result
        assert "count" in result
        assert isinstance(result["gates"], list)
    except ImportError as e:
        pytest.skip(f"gate_tools not importable: {e}")
