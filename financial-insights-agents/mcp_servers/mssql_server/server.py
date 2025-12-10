"""MSSQL MCP Server implementation."""

import asyncio
import logging
from typing import Any

from mcp import types
from mcp.server import Server
from mcp.server.stdio import stdio_server
from sqlalchemy.exc import SQLAlchemyError

from .connection_pool import DatabaseConnectionPool

logger = logging.getLogger(__name__)


class MSSQLMCPServer:
    """MCP Server for MSSQL database operations."""

    def __init__(self, connection_string: str) -> None:
        """Initialize MSSQL MCP Server.

        Args:
            connection_string: SQLAlchemy connection string for MSSQL
        """
        self.connection_string = connection_string
        self.db_pool = DatabaseConnectionPool(connection_string)
        self.server = Server("mssql-server")

        # Register tools
        self._register_tools()

        logger.info("MSSQL MCP Server initialized")

    def _register_tools(self) -> None:
        """Register all MCP tools."""

        @self.server.list_tools()
        async def list_tools() -> list[types.Tool]:
            """List available tools."""
            return [
                types.Tool(
                    name="execute_sql_query",
                    description="Execute a SQL query on the MSSQL database and return results",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "SQL query to execute",
                            },
                            "params": {
                                "type": "object",
                                "description": "Optional query parameters as key-value pairs",
                                "default": {},
                            },
                            "timeout": {
                                "type": "integer",
                                "description": "Query timeout in seconds",
                                "default": 30,
                            },
                        },
                        "required": ["query"],
                    },
                ),
                types.Tool(
                    name="get_database_schema",
                    description="Get schema information for database tables",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "table_name": {
                                "type": "string",
                                "description": "Specific table name (optional, returns all tables if not provided)",
                            },
                        },
                    },
                ),
                types.Tool(
                    name="get_table_sample",
                    description="Get sample rows from a specific table",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "table_name": {
                                "type": "string",
                                "description": "Name of the table to sample",
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Number of rows to return",
                                "default": 5,
                            },
                        },
                        "required": ["table_name"],
                    },
                ),
                types.Tool(
                    name="validate_sql_query",
                    description="Validate SQL query syntax without executing it",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "SQL query to validate",
                            },
                        },
                        "required": ["query"],
                    },
                ),
                types.Tool(
                    name="get_table_names",
                    description="Get list of all table names in the database",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
                types.Tool(
                    name="test_connection",
                    description="Test database connection status",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
                types.Tool(
                    name="get_pool_status",
                    description="Get current database connection pool status",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(
            name: str, arguments: dict[str, Any]
        ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
            """Handle tool calls."""
            logger.info(f"Tool called: {name}")

            try:
                if name == "execute_sql_query":
                    return await self._execute_query_tool(arguments)
                elif name == "get_database_schema":
                    return await self._get_schema_tool(arguments)
                elif name == "get_table_sample":
                    return await self._get_sample_tool(arguments)
                elif name == "validate_sql_query":
                    return await self._validate_query_tool(arguments)
                elif name == "get_table_names":
                    return await self._get_table_names_tool()
                elif name == "test_connection":
                    return await self._test_connection_tool()
                elif name == "get_pool_status":
                    return await self._get_pool_status_tool()
                else:
                    raise ValueError(f"Unknown tool: {name}")

            except Exception as e:
                logger.error(f"Tool execution error ({name}): {e}")
                return [
                    types.TextContent(
                        type="text",
                        text=f"Error executing tool {name}: {str(e)}",
                    )
                ]

    async def _execute_query_tool(
        self, arguments: dict[str, Any]
    ) -> list[types.TextContent]:
        """Execute SQL query tool implementation."""
        query = arguments.get("query", "")
        params = arguments.get("params", {})

        # Security: Prevent dangerous operations
        query_upper = query.upper().strip()
        dangerous_keywords = ["DROP", "TRUNCATE", "ALTER", "DELETE"]
        if any(keyword in query_upper for keyword in dangerous_keywords):
            return [
                types.TextContent(
                    type="text",
                    text=f"Error: Query contains dangerous keywords. Only SELECT queries are allowed in MVP.",
                )
            ]

        try:
            # Execute query in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None, self.db_pool.execute_query, query, params
            )

            # Format results
            result_text = f"Query executed successfully. Returned {len(results)} rows.\n\n"
            if results:
                result_text += str(results)
            else:
                result_text += "No rows returned."

            return [types.TextContent(type="text", text=result_text)]

        except SQLAlchemyError as e:
            return [
                types.TextContent(
                    type="text",
                    text=f"Database error: {str(e)}",
                )
            ]

    async def _get_schema_tool(
        self, arguments: dict[str, Any]
    ) -> list[types.TextContent]:
        """Get database schema tool implementation."""
        table_name = arguments.get("table_name")

        try:
            loop = asyncio.get_event_loop()

            if table_name:
                # Get schema for specific table
                schema = await loop.run_in_executor(
                    None, self.db_pool.get_table_schema, table_name
                )
                result_text = f"Schema for table '{table_name}':\n\n"
                result_text += str(schema)
            else:
                # Get all table names
                tables = await loop.run_in_executor(None, self.db_pool.get_table_names)
                result_text = f"Database tables ({len(tables)}):\n\n"
                result_text += "\n".join(f"- {table}" for table in tables)

            return [types.TextContent(type="text", text=result_text)]

        except SQLAlchemyError as e:
            return [
                types.TextContent(
                    type="text",
                    text=f"Database error: {str(e)}",
                )
            ]

    async def _get_sample_tool(
        self, arguments: dict[str, Any]
    ) -> list[types.TextContent]:
        """Get table sample tool implementation."""
        table_name = arguments.get("table_name")
        limit = arguments.get("limit", 5)

        try:
            loop = asyncio.get_event_loop()
            sample = await loop.run_in_executor(
                None, self.db_pool.get_table_sample, table_name, limit
            )

            result_text = f"Sample data from '{table_name}' (limit={limit}):\n\n"
            result_text += str(sample)

            return [types.TextContent(type="text", text=result_text)]

        except SQLAlchemyError as e:
            return [
                types.TextContent(
                    type="text",
                    text=f"Database error: {str(e)}",
                )
            ]

    async def _validate_query_tool(
        self, arguments: dict[str, Any]
    ) -> list[types.TextContent]:
        """Validate SQL query tool implementation."""
        query = arguments.get("query", "")

        # Basic validation
        errors = []

        if not query.strip():
            errors.append("Query is empty")

        query_upper = query.upper().strip()

        # Check for dangerous keywords
        dangerous_keywords = ["DROP", "TRUNCATE", "ALTER"]
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                errors.append(f"Query contains dangerous keyword: {keyword}")

        # Check for basic SQL syntax
        if not query_upper.startswith(("SELECT", "WITH", "EXEC", "INSERT", "UPDATE")):
            errors.append("Query must start with a valid SQL keyword")

        # Check for balanced parentheses
        if query.count("(") != query.count(")"):
            errors.append("Unbalanced parentheses in query")

        # Check for balanced quotes
        if query.count("'") % 2 != 0:
            errors.append("Unbalanced single quotes in query")

        if errors:
            result_text = "Query validation failed:\n\n"
            result_text += "\n".join(f"- {error}" for error in errors)
        else:
            result_text = "Query validation passed. Basic syntax checks successful."

        return [types.TextContent(type="text", text=result_text)]

    async def _get_table_names_tool(self) -> list[types.TextContent]:
        """Get table names tool implementation."""
        try:
            loop = asyncio.get_event_loop()
            tables = await loop.run_in_executor(None, self.db_pool.get_table_names)

            result_text = f"Database tables ({len(tables)}):\n\n"
            result_text += "\n".join(f"- {table}" for table in tables)

            return [types.TextContent(type="text", text=result_text)]

        except SQLAlchemyError as e:
            return [
                types.TextContent(
                    type="text",
                    text=f"Database error: {str(e)}",
                )
            ]

    async def _test_connection_tool(self) -> list[types.TextContent]:
        """Test connection tool implementation."""
        try:
            loop = asyncio.get_event_loop()
            is_connected = await loop.run_in_executor(None, self.db_pool.test_connection)

            if is_connected:
                result_text = "Database connection test: SUCCESS"
            else:
                result_text = "Database connection test: FAILED"

            return [types.TextContent(type="text", text=result_text)]

        except Exception as e:
            return [
                types.TextContent(
                    type="text",
                    text=f"Connection test error: {str(e)}",
                )
            ]

    async def _get_pool_status_tool(self) -> list[types.TextContent]:
        """Get pool status tool implementation."""
        try:
            loop = asyncio.get_event_loop()
            status = await loop.run_in_executor(None, self.db_pool.get_pool_status)

            result_text = "Database Connection Pool Status:\n\n"
            result_text += f"- Pool Size: {status['size']}\n"
            result_text += f"- Checked In: {status['checked_in']}\n"
            result_text += f"- Checked Out: {status['checked_out']}\n"
            result_text += f"- Overflow: {status['overflow']}\n"
            result_text += f"- Total Connections: {status['total_connections']}\n"

            return [types.TextContent(type="text", text=result_text)]

        except Exception as e:
            return [
                types.TextContent(
                    type="text",
                    text=f"Pool status error: {str(e)}",
                )
            ]

    async def run(self) -> None:
        """Run the MCP server."""
        logger.info("Starting MSSQL MCP Server...")

        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options(),
            )

    def close(self) -> None:
        """Close server and database connections."""
        logger.info("Closing MSSQL MCP Server")
        self.db_pool.close()


async def main() -> None:
    """Main entry point for MCP server."""
    import os
    from dotenv import load_dotenv

    load_dotenv()

    connection_string = os.getenv("MSSQL_CONNECTION_STRING")
    if not connection_string:
        raise ValueError("MSSQL_CONNECTION_STRING environment variable not set")

    server = MSSQLMCPServer(connection_string)

    try:
        await server.run()
    finally:
        server.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
