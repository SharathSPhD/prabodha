"""prabodha MCP server — tool definitions and stdio dispatch.

Concept: operational steering access via Model Context Protocol (mcp.dev).
Source: WS3 plan (closure master plan, spec §3).
Primitive: stdio MCP server spawning prabodha CLI tools.
"""
import json
import subprocess
import sys
from typing import Any
import logging

from mcp.server import Server
from mcp.types import Tool, TextContent, CallToolResult


logger = logging.getLogger(__name__)


server = Server("prabodha-mcp")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """Expose the four operational steering tools."""
    return [
        Tool(
            name="lens_map",
            description=(
                "Fit and evaluate a band-targeted Jacobian lens on a HuggingFace model. "
                "Runs fit → eval → optional vis end-to-end. "
                "Default gate: gates/gate_L13_recipe.json (band readback correspondence structure). "
                "Requires: model_config (path to configs/models/*.yaml), "
                "lens_config (configs/lens.yaml), output_dir (e.g. outputs/). "
                "Optional: prompt (for visualization)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "model_config": {
                        "type": "string",
                        "description": "Path to model config YAML (e.g., configs/models/Qwen3-4B.yaml)",
                    },
                    "lens_config": {
                        "type": "string",
                        "description": "Path to lens config YAML (e.g., configs/lens.yaml)",
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "Output directory for fitted lens checkpoint and gate JSON",
                    },
                    "prompt": {
                        "type": "string",
                        "description": "Optional prompt for visualization slice page",
                    },
                },
                "required": ["model_config", "lens_config", "output_dir"],
            },
        ),
        Tool(
            name="steer_generate",
            description=(
                "Run a steering episode: fit band lens, apply recognition-gated writes, "
                "return full SteerTrace JSON. "
                "Default gate: gates/gate_L9_alignconf.json (arm/seed semantics from L9). "
                "Requires: model_config (path to configs/models/*.yaml), concept (e.g., 'fire'), "
                "prompt (seed text). Optional: arm (entropy_gated|baseline|...), seed (42|123|777), "
                "alpha (write amplitude), tau_percentile (entropy gate threshold). "
                "Returns: JSON SteerTrace with per-token entropy, write norms, band readout, readback verdict."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "model_config": {
                        "type": "string",
                        "description": "Path to model config YAML",
                    },
                    "concept": {
                        "type": "string",
                        "description": "Steering concept (e.g., 'fire', 'water')",
                    },
                    "prompt": {
                        "type": "string",
                        "description": "Seed prompt for the episode",
                    },
                    "arm": {
                        "type": "string",
                        "description": "Steering arm: baseline|prefill|entropy_gated|rate_matched|continuous|trained_bridge",
                        "default": "entropy_gated",
                    },
                    "seed": {
                        "type": "integer",
                        "description": "Random seed (42, 123, or 777 for clean stream)",
                        "default": 42,
                    },
                    "alpha": {
                        "type": "number",
                        "description": "Write amplitude (calibrated inversely to lens transport strength)",
                        "default": 0.3,
                    },
                    "tau_percentile": {
                        "type": "integer",
                        "description": "Entropy percentile threshold for gating (0–100)",
                        "default": 60,
                    },
                },
                "required": ["model_config", "concept", "prompt"],
            },
        ),
        Tool(
            name="readback_verify",
            description=(
                "Run readback verification on a completed steering trace. "
                "Returns: readback verdict (accepted|rejected), top_m, gain, concept_rank. "
                "CAVEAT (weak-signal honest negative): readback is probabilistic and noisy; "
                "single runs are not confirmatory. Multi-seed readback at confirm tier required. "
                "Default gate: gates/gate_L14_readback.json (readback method + thresholds). "
                "Requires: trace_json_path (path to output trace from steer_generate)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "trace_json_path": {
                        "type": "string",
                        "description": "Path to SteerTrace JSON file (output from steer_generate)",
                    },
                },
                "required": ["trace_json_path"],
            },
        ),
        Tool(
            name="list_gates",
            description=(
                "Enumerate all committed gates in gates/*.json with their verdicts and gate_refs. "
                "Useful for discovering available claim gates and their paths. "
                "No authentication required."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "filter_arm": {
                        "type": "string",
                        "description": "Optional filter by arm (e.g., 'entropy_gated')",
                    },
                    "filter_concept": {
                        "type": "string",
                        "description": "Optional filter by concept (e.g., 'fire')",
                    },
                },
                "required": [],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[CallToolResult]:
    """Dispatch tool calls to implementations in tools/ modules."""
    try:
        if name == "lens_map":
            from .tools.lens_tools import lens_map_impl
            result = await lens_map_impl(**arguments)
        elif name == "steer_generate":
            from .tools.steer_tools import steer_generate_impl
            result = await steer_generate_impl(**arguments)
        elif name == "readback_verify":
            from .tools.gate_tools import readback_verify_impl
            result = await readback_verify_impl(**arguments)
        elif name == "list_gates":
            from .tools.gate_tools import list_gates_impl
            result = await list_gates_impl(**arguments)
        else:
            return [CallToolResult(content=[TextContent(type="text", text=f"Unknown tool: {name}")])]

        return [CallToolResult(content=[TextContent(type="text", text=json.dumps(result))])]
    except Exception as e:
        logger.exception(f"Tool {name} failed")
        return [CallToolResult(content=[TextContent(type="text", text=f"Error: {e}")])]


async def main():
    """Entry point: start the MCP server on stdio."""
    async with server:
        # Server starts and waits for client messages on stdio.
        pass


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
