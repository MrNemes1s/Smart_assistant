"""Configuration management using Pydantic Settings."""

from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Azure AI Foundry
    azure_ai_project_connection_string: str = ""
    azure_ai_project_id: str = ""
    azure_resource_group: str = ""
    azure_subscription_id: str = ""

    # Azure OpenAI / Claude
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_deployment_name: str = "claude-3-5-sonnet"
    azure_openai_api_version: str = "2024-02-15-preview"

    # Alternative: Direct Anthropic API
    anthropic_api_key: str = ""

    # MSSQL Database
    mssql_server: str = "localhost"
    mssql_port: int = 1433
    mssql_database: str = "financial_insights_db"
    mssql_username: str = "sa"
    mssql_password: str = ""
    mssql_driver: str = "ODBC Driver 18 for SQL Server"
    mssql_trust_server_certificate: str = "yes"

    @property
    def mssql_connection_string(self) -> str:
        """Generate MSSQL connection string."""
        return (
            f"mssql+pyodbc://{self.mssql_username}:{self.mssql_password}"
            f"@{self.mssql_server}:{self.mssql_port}/{self.mssql_database}"
            f"?driver={self.mssql_driver.replace(' ', '+')}"
            f"&TrustServerCertificate={self.mssql_trust_server_certificate}"
        )

    # MCP Server
    mcp_server_host: str = "localhost"
    mcp_server_port: int = 8080
    mcp_server_protocol: str = "http"

    @property
    def mcp_server_url(self) -> str:
        """Generate MCP server URL."""
        return f"{self.mcp_server_protocol}://{self.mcp_server_host}:{self.mcp_server_port}"

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True
    api_workers: int = 1
    api_log_level: str = "info"

    # Security
    secret_key: str = Field(default="your-secret-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Validate secret key is set in production."""
        if len(v) < 32:
            raise ValueError("Secret key must be at least 32 characters long")
        return v

    # Azure Key Vault
    azure_key_vault_name: str = ""
    azure_key_vault_url: str = ""

    # Agent Configuration
    sql_agent_model: str = "claude-3-5-sonnet"
    sql_agent_temperature: float = 0.1
    sql_agent_max_tokens: int = 2048

    analyst_agent_model: str = "claude-3-5-sonnet"
    analyst_agent_temperature: float = 0.3
    analyst_agent_max_tokens: int = 4096

    expert_agent_model: str = "claude-3-5-sonnet"
    expert_agent_temperature: float = 0.5
    expert_agent_max_tokens: int = 4096

    # Code Interpreter
    code_interpreter_timeout: int = 300
    code_interpreter_max_memory_mb: int = 2048

    # Logging
    log_level: str = "INFO"
    log_format: Literal["json", "text"] = "json"
    log_file: str = "logs/app.log"

    # Observability
    enable_telemetry: bool = False
    otel_exporter_otlp_endpoint: str = ""
    applicationinsights_connection_string: str = ""

    # Development
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = True

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment == "development"


# Global settings instance
settings = Settings()
