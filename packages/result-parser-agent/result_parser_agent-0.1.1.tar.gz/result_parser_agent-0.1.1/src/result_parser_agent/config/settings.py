"""Configuration management for the results parser agent."""

import os
from pathlib import Path

from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings


class LLMConfig(BaseModel):
    """Configuration for LLM providers."""

    provider: str = Field(
        default="google",
        description="LLM provider (groq, openai, anthropic, ollama, google)",
    )
    model: str = Field(default="gemini-2.0-flash", description="LLM model to use")
    api_key: str | None = Field(
        default=None, description="API key for the LLM provider"
    )
    temperature: float = Field(default=0.1, description="Temperature for LLM responses")
    max_tokens: int = Field(default=4000, description="Maximum tokens for responses")
    base_url: str | None = Field(
        default=None, description="Base URL for local LLM server (e.g., Ollama)"
    )


class AgentConfig(BaseModel):
    """Configuration for the agent behavior."""

    llm: LLMConfig = Field(default_factory=LLMConfig)
    max_retries: int = Field(
        default=3, description="Maximum number of retries for failed operations"
    )
    chunk_size: int = Field(default=2000, description="Size of file chunks to process")
    timeout: int = Field(default=300, description="Timeout for operations in seconds")
    debug: bool = Field(
        default=False,
        description="Enable debug mode to show intermediate steps and tool executions",
    )


class ParsingConfig(BaseModel):
    """Configuration for parsing behavior."""

    metrics: list[str] = Field(..., description="List of metrics to extract")
    case_sensitive: bool = Field(
        default=False, description="Whether pattern matching is case sensitive"
    )
    fuzzy_match: bool = Field(default=True, description="Whether to use fuzzy matching")
    min_confidence: float = Field(
        default=0.7, description="Minimum confidence for metric extraction"
    )


class OutputConfig(BaseModel):
    """Configuration for output formatting."""

    format: str = Field(default="json", description="Output format (json, csv, yaml)")
    pretty_print: bool = Field(
        default=True, description="Whether to pretty print output"
    )
    include_metadata: bool = Field(
        default=True, description="Whether to include metadata in output"
    )


class LoggingConfig(BaseModel):
    """Configuration for logging."""

    level: str = Field(default="INFO", description="Logging level")
    format: str = Field(
        default="{time} | {level} | {message}", description="Log format"
    )
    file: str | None = Field(default=None, description="Log file path")


class ParserConfig(BaseSettings):
    """Main configuration class for the results parser agent."""

    agent: AgentConfig = Field(default_factory=AgentConfig)
    parsing: ParsingConfig = Field(..., description="Parsing configuration")
    output: OutputConfig = Field(default_factory=OutputConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)

    # Environment variable settings
    class Config:
        env_prefix = "PARSER_"
        env_nested_delimiter = "__"

    @validator("parsing")
    def validate_parsing_config(cls, v: ParsingConfig) -> ParsingConfig:
        """Validate parsing configuration."""
        if not v.metrics:
            raise ValueError("At least one metric must be specified")
        return v

    def get_llm_config(self) -> dict[str, str]:
        """Get LLM configuration with API key resolution."""
        llm_config = self.agent.llm.model_dump()

        # Resolve API key from environment if not provided
        if not llm_config["api_key"]:
            provider = llm_config["provider"].upper()
            env_key = f"{provider}_API_KEY"
            llm_config["api_key"] = os.getenv(env_key)

            if not llm_config["api_key"]:
                raise ValueError(
                    f"API key not found. Set {env_key} environment variable or provide in config."
                )

        return llm_config

    @classmethod
    def from_yaml(cls, yaml_path: str | Path) -> "ParserConfig":
        """Load configuration from YAML file."""
        import yaml

        with open(yaml_path) as f:
            config_data = yaml.safe_load(f)

        return cls(**config_data)

    def to_yaml(self, yaml_path: str | Path) -> None:
        """Save configuration to YAML file."""
        import yaml

        with open(yaml_path, "w") as f:
            yaml.dump(self.model_dump(), f, default_flow_style=False, indent=2)


# Default configuration with Google Gemini
DEFAULT_CONFIG = ParserConfig(
    agent=AgentConfig(
        llm=LLMConfig(
            provider="google",
            model="gemini-2.0-flash",
            temperature=0.1,
            api_key=os.getenv("GOOGLE_API_KEY"),
        )
    ),
    parsing=ParsingConfig(metrics=["RPS", "latency", "throughput"]),
)
