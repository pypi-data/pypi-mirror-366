"""Configuration management for MOA SDK."""

import os
from enum import Enum
from typing import Optional
from urllib.parse import urljoin

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Environment(str, Enum):
    """Supported MOA API environments."""

    ALPHA = "alpha"
    BETA = "beta"
    PRODUCTION = "production"


class Config(BaseModel):
    """Configuration for MOA SDK."""

    # API Configuration
    api_key: str = Field(..., description="MOA API key")
    environment: Environment = Field(Environment.BETA, description="API environment")
    api_version: str = Field("v1", description="API version")

    # Network Configuration
    timeout: float = Field(30.0, description="Request timeout in seconds")
    max_retries: int = Field(3, description="Maximum number of retries")
    retry_delay: float = Field(1.0, description="Delay between retries in seconds")

    # Advanced Configuration
    user_agent: Optional[str] = Field(None, description="Custom user agent")
    debug: bool = Field(False, description="Enable debug mode")

    model_config = ConfigDict(env_prefix="MOA_", case_sensitive=False)

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate API key format."""
        if not v or not v.strip():
            raise ValueError("API key cannot be empty")
        return v.strip()

    @field_validator("timeout")
    @classmethod
    def validate_timeout(cls, v: float) -> float:
        """Validate timeout value."""
        if v <= 0:
            raise ValueError("Timeout must be positive")
        return v

    @field_validator("max_retries")
    @classmethod
    def validate_max_retries(cls, v: int) -> int:
        """Validate max retries value."""
        if v < 0:
            raise ValueError("Max retries cannot be negative")
        return v

    @property
    def base_url(self) -> str:
        """Get the base URL for the configured environment."""
        url_mapping = {
            Environment.ALPHA: "https://api.alpha.memof.ai",
            Environment.BETA: "https://beta-api.memof.ai",
            Environment.PRODUCTION: "https://api.memof.ai",
        }
        return url_mapping[self.environment]

    @property
    def api_base_url(self) -> str:
        """Get the API base URL with version."""
        return urljoin(self.base_url, f"/api/{self.api_version}/")

    @classmethod
    def from_env(cls, **overrides) -> "Config":
        """Create config from environment variables with optional overrides."""
        # Try to get API key from environment if not provided
        api_key = overrides.get("api_key") or os.getenv("MOA_API_KEY")
        if not api_key:
            raise ValueError(
                "API key is required. Set MOA_API_KEY environment variable or "
                "pass api_key parameter."
            )

        # Get environment setting
        env_name = overrides.get("environment") or os.getenv("MOA_ENVIRONMENT", "beta")
        if isinstance(env_name, str):
            try:
                environment = Environment(env_name.lower())
            except ValueError as e:
                valid_envs = ["alpha", "beta", "production"]
                raise ValueError(
                    f"Invalid environment: {env_name}. " f"Valid options: {valid_envs}"
                ) from e
        else:
            environment = env_name

        # Create config with environment variables and overrides
        config_data = {
            "api_key": api_key,
            "environment": environment,
            "api_version": os.getenv("MOA_API_VERSION", "v1"),
            "timeout": float(os.getenv("MOA_TIMEOUT", "30.0")),
            "max_retries": int(os.getenv("MOA_MAX_RETRIES", "3")),
            "retry_delay": float(os.getenv("MOA_RETRY_DELAY", "1.0")),
            "debug": os.getenv("MOA_DEBUG", "false").lower() == "true",
        }

        # Apply overrides
        config_data.update(overrides)

        return cls(**config_data)
