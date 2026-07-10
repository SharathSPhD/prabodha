"""MCP server entry point for module execution.

Allows the server to be invoked as: python -m prabodha_mcp_server
"""
from server import main
import asyncio


if __name__ == "__main__":
    asyncio.run(main())
