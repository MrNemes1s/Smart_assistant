"""MCP Client for agents to communicate with MCP servers."""

import asyncio
import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class MCPClient:
    """Client for communicating with MCP servers."""

    def __init__(self, server_url: str, timeout: int = 30) -> None:
        """Initialize MCP client.

        Args:
            server_url: URL of the MCP server
            timeout: Request timeout in seconds
        """
        self.server_url = server_url.rstrip("/")
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None

        logger.info(f"MCP Client initialized for server: {server_url}")

    async def __aenter__(self) -> "MCPClient":
        """Async context manager entry."""
        self._client = httpx.AsyncClient(timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()

    @property
    def client(self) -> httpx.AsyncClient:
        """Get HTTP client, creating if needed."""
        if self._client is None:
            raise RuntimeError("MCPClient must be used as an async context manager")
        return self._client

    async def call_tool(
        self, tool_name: str, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Call a tool on the MCP server.

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments

        Returns:
            Tool response

        Raises:
            httpx.HTTPError: If request fails
        """
        logger.debug(f"Calling MCP tool: {tool_name}")

        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments,
            },
        }

        try:
            response = await self.client.post(
                f"{self.server_url}/rpc",
                json=payload,
            )
            response.raise_for_status()

            result = response.json()

            if "error" in result:
                error_msg = result["error"].get("message", "Unknown error")
                logger.error(f"MCP tool error: {error_msg}")
                raise RuntimeError(f"MCP tool error: {error_msg}")

            logger.debug(f"MCP tool {tool_name} executed successfully")
            return result.get("result", {})

        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling MCP tool: {e}")
            raise

    async def list_tools(self) -> list[dict[str, Any]]:
        """List available tools on the MCP server.

        Returns:
            List of available tools

        Raises:
            httpx.HTTPError: If request fails
        """
        logger.debug("Listing MCP tools")

        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {},
        }

        try:
            response = await self.client.post(
                f"{self.server_url}/rpc",
                json=payload,
            )
            response.raise_for_status()

            result = response.json()

            if "error" in result:
                error_msg = result["error"].get("message", "Unknown error")
                logger.error(f"Error listing tools: {error_msg}")
                raise RuntimeError(f"Error listing tools: {error_msg}")

            tools = result.get("result", {}).get("tools", [])
            logger.info(f"Found {len(tools)} available tools")
            return tools

        except httpx.HTTPError as e:
            logger.error(f"HTTP error listing tools: {e}")
            raise

    async def execute_query(
        self, query: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Execute SQL query via MCP server.

        Args:
            query: SQL query to execute
            params: Optional query parameters

        Returns:
            Query results
        """
        logger.debug(f"Executing query via MCP: {query[:100]}...")

        result = await self.call_tool(
            "execute_sql_query",
            {"query": query, "params": params or {}},
        )

        # Parse results from MCP response
        content = result.get("content", [])
        if content and isinstance(content, list):
            text_content = content[0].get("text", "")
            # Simple parsing - in production, use structured response
            return [{"result": text_content}]

        return []

    async def get_database_schema(
        self, table_name: str | None = None
    ) -> dict[str, Any]:
        """Get database schema via MCP server.

        Args:
            table_name: Optional specific table name

        Returns:
            Schema information
        """
        logger.debug(f"Getting database schema: {table_name or 'all tables'}")

        arguments = {}
        if table_name:
            arguments["table_name"] = table_name

        result = await self.call_tool("get_database_schema", arguments)

        # Parse results from MCP response
        content = result.get("content", [])
        if content and isinstance(content, list):
            text_content = content[0].get("text", "")
            return {"schema": text_content}

        return {}

    async def get_table_sample(
        self, table_name: str, limit: int = 5
    ) -> list[dict[str, Any]]:
        """Get table sample via MCP server.

        Args:
            table_name: Table name
            limit: Number of rows

        Returns:
            Sample rows
        """
        logger.debug(f"Getting table sample: {table_name} (limit={limit})")

        result = await self.call_tool(
            "get_table_sample",
            {"table_name": table_name, "limit": limit},
        )

        # Parse results from MCP response
        content = result.get("content", [])
        if content and isinstance(content, list):
            text_content = content[0].get("text", "")
            return [{"sample": text_content}]

        return []

    async def test_connection(self) -> bool:
        """Test database connection via MCP server.

        Returns:
            True if connection successful
        """
        logger.debug("Testing database connection")

        try:
            result = await self.call_tool("test_connection", {})
            content = result.get("content", [])
            if content and isinstance(content, list):
                text_content = content[0].get("text", "")
                return "SUCCESS" in text_content

            return False

        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False


# Example usage
async def main() -> None:
    """Example usage of MCP client."""
    async with MCPClient("http://localhost:8080") as client:
        # Test connection
        is_connected = await client.test_connection()
        print(f"Connection test: {is_connected}")

        # List tools
        tools = await client.list_tools()
        print(f"Available tools: {len(tools)}")

        # Get schema
        schema = await client.get_database_schema()
        print(f"Database schema: {schema}")

        # Execute query
        results = await client.execute_query("SELECT TOP 5 * FROM dbo.portfolios")
        print(f"Query results: {results}")


if __name__ == "__main__":
    asyncio.run(main())
