# prabodha MCP Server

A Model Context Protocol (MCP) server providing access to prabodha's steering and lens-fitting tools.

## Installation

```bash
pip install -e .  # or: pip install prabodha-mcp-server
```

## Running

```bash
prabodha-mcp
```

This starts the server on stdio; connect via any MCP client.

## Tools

- `lens_map`: Fit and evaluate a band-targeted Jacobian lens
- `steer_generate`: Run a steering episode and return trace
- `readback_verify`: Run readback verification on a completed trace
- `list_gates`: Enumerate committed gates in the repository

See `server.py` for detailed tool schemas and default gate citations.
