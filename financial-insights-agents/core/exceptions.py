"""Custom exceptions for the financial insights agents system."""


class AgentError(Exception):
    """Base exception for all agent-related errors."""

    def __init__(self, message: str, agent_name: str | None = None) -> None:
        self.message = message
        self.agent_name = agent_name
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.agent_name:
            return f"[{self.agent_name}] {self.message}"
        return self.message


class ConfigurationError(AgentError):
    """Raised when there is a configuration error."""

    pass


class DatabaseError(AgentError):
    """Raised when there is a database-related error."""

    def __init__(self, message: str, query: str | None = None) -> None:
        super().__init__(message)
        self.query = query


class MCPError(AgentError):
    """Raised when there is an MCP server communication error."""

    def __init__(self, message: str, mcp_tool: str | None = None) -> None:
        super().__init__(message)
        self.mcp_tool = mcp_tool


class OrchestrationError(AgentError):
    """Raised when there is an orchestration error."""

    def __init__(
        self, message: str, failed_agent: str | None = None, context: dict | None = None
    ) -> None:
        super().__init__(message, agent_name=failed_agent)
        self.context = context or {}


class ToolExecutionError(AgentError):
    """Raised when a tool execution fails."""

    def __init__(self, message: str, tool_name: str, error_details: dict | None = None) -> None:
        super().__init__(message)
        self.tool_name = tool_name
        self.error_details = error_details or {}


class ValidationError(AgentError):
    """Raised when input validation fails."""

    def __init__(self, message: str, field: str | None = None, value: str | None = None) -> None:
        super().__init__(message)
        self.field = field
        self.value = value


class AuthenticationError(AgentError):
    """Raised when authentication fails."""

    pass


class RateLimitError(AgentError):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str, retry_after: int | None = None) -> None:
        super().__init__(message)
        self.retry_after = retry_after
