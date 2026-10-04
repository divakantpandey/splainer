"""Application configuration for spl-to-sql.

Uses pydantic-settings to load configuration from environment variables.
No hardcoded secrets — all sensitive values (API keys, DB connection strings)
flow through environment variables.

TODO: Add schema/ module or config section for mapping Splunk index/sourcetype
      metadata to SQL table/column names once the design is finalized.
"""

import logging
from enum import StrEnum

from pydantic import SecretStr
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class SqlDialect(StrEnum):
    """Supported SQL target dialects.

    TODO: Add more dialects as codegen/dialects/ modules are implemented.
    """

    POSTGRES = "postgres"
    SNOWFLAKE = "snowflake"
    MYSQL = "mysql"


class LLMProviderConfig(BaseSettings):
    """Configuration for the LLM provider used in fallback codegen.

    Attributes:
        api_key: API key for the LLM provider. Loaded from LLM_API_KEY env var.
        model_name: Model identifier (e.g., 'gpt-4', 'claude-3-opus').
        base_url: Optional custom API base URL.
        max_tokens: Maximum tokens in the LLM response.
        temperature: Sampling temperature for generation.

    TODO: Implement provider-specific subclasses if needed.
    """

    model_config = {"env_prefix": "LLM_"}

    api_key: SecretStr = SecretStr("")
    model_name: str = "gpt-4"
    base_url: str | None = None
    max_tokens: int = 2048
    temperature: float = 0.0


class RetryConfig(BaseSettings):
    """Configuration for the execution retry/feedback loop.

    Attributes:
        max_attempts: Maximum number of retry attempts.
        base_delay_seconds: Base delay for exponential backoff.
        max_delay_seconds: Maximum delay cap for backoff.
        jitter: Whether to add random jitter to backoff delays.

    TODO: Implement actual backoff logic in execution/retry.py.
    """

    model_config = {"env_prefix": "RETRY_"}

    max_attempts: int = 3
    base_delay_seconds: float = 1.0
    max_delay_seconds: float = 60.0
    jitter: bool = True



class AgentConfig(BaseSettings):
    """Configuration for agent pipeline behavior.

    Attributes:
        enabled: Whether to use agent-based orchestration.
        max_fix_attempts: Maximum LLM fix attempts per agent.
        console_tree_enabled: Show Rich console tree output.

    """

    model_config = {"env_prefix": "AGENT_"}

    enabled: bool = True
    max_fix_attempts: int = 3
    console_tree_enabled: bool = True


class DatabaseConfig(BaseSettings):
    """Configuration for the target database connection.

    Attributes:
        connection_string: Database connection string. Loaded from DB_CONNECTION_STRING.
        schema_name: Default schema/namespace to use.
        timeout_seconds: Query execution timeout.

    TODO: Implement connection pooling configuration.
    """

    model_config = {"env_prefix": "DB_"}

    connection_string: SecretStr = SecretStr("")
    schema_name: str = "public"
    timeout_seconds: int = 30


class SplToSqlConfig(BaseSettings):
    """Top-level application configuration.

    Attributes:
        dialect: Target SQL dialect for code generation.
        llm: LLM provider configuration.
        retry: Retry/backoff configuration.
        database: Target database configuration.
        log_level: Logging level.

    TODO: Implement configuration file loading (e.g., from ~/.spl-to-sql/config.toml).
    """

    model_config = {
        "env_prefix": "SPL_TO_SQL_",
        "env_nested_delimiter": "__",
        "env_file": "infra/.env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    dialect: SqlDialect = SqlDialect.POSTGRES
    from pydantic import Field
    
    llm: LLMProviderConfig | None = None
    retry: RetryConfig = Field(default_factory=RetryConfig)
    agent: AgentConfig = Field(default_factory=AgentConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    log_level: str = "WARNING"

    @classmethod
    def from_env(cls) -> "SplToSqlConfig":
        """Load configuration from environment variables."""
        import dotenv
        from pathlib import Path
        
        # Load the infra/.env file globally so all nested Configs (like DatabaseConfig)
        # can read their specific prefixes (e.g. DB_CONNECTION_STRING).
        env_path = Path(__file__).parent.parent.parent / "infra" / ".env"
        dotenv.load_dotenv(env_path)
        
        return cls()
