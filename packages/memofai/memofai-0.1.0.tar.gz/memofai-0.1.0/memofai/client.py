"""Main MOA SDK client."""

from typing import Any, Dict, Optional, Union

from .api import GraphSearchAPI, MemoryAPI, RelationshipsAPI
from .config import Config, Environment
from .models.base import HealthResponse
from .utils.http import HTTPClient


class MOAClient:
    """Main client for interacting with the MOA API.

    The MOAClient provides a comprehensive interface to the Memory Of Agents API,
    supporting memory operations, graph search, and relationship management.

    Example:
        Basic usage:
        ```python
        from memofai import MOAClient, Environment

        # Initialize with environment and API key
        client = MOAClient(
            api_key="your-api-key",
            environment=Environment.BETA
        )

        # Create a memory
        response = client.memory.create_memory({
            "content": "Important information to remember",
            "tags": ["important", "meeting"],
            "metadata": {"source": "meeting notes"}
        })

        # Search memories
        results = client.memory.search_memories(
            query="meeting notes",
            max_results=10
        )

        # Perform graph search
        graph_results = client.graph.search_shortest_path(
            query="project updates",
            max_depth=3
        )
        ```

        Async usage:
        ```python
        import asyncio
        from memofai import MOAClient

        async def main():
            client = MOAClient(api_key="your-api-key")

            # Async memory operations
            response = await client.memory.acreate_memory({
                "content": "Async memory creation"
            })

            # Don't forget to close the client
            await client.aclose()

        asyncio.run(main())
        ```
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        environment: Union[Environment, str] = Environment.BETA,
        api_version: str = "v1",
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        debug: bool = False,
        **kwargs,
    ):
        """Initialize the MOA client.

        Args:
            api_key: MOA API key. If not provided, will try to get from MOA_API_KEY env var
            environment: API environment (alpha, beta, production)
            api_version: API version to use
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            retry_delay: Delay between retries in seconds
            debug: Enable debug mode for detailed logging
            **kwargs: Additional configuration options
        """
        # Create configuration
        config_kwargs = {
            "environment": environment,
            "api_version": api_version,
            "timeout": timeout,
            "max_retries": max_retries,
            "retry_delay": retry_delay,
            "debug": debug,
            **kwargs,
        }

        if api_key:
            config_kwargs["api_key"] = api_key

        self.config = Config.from_env(**config_kwargs)

        # Initialize HTTP client
        self._http_client = HTTPClient(self.config)

        # Initialize API clients
        self.memory = MemoryAPI(self._http_client)
        self.graph = GraphSearchAPI(self._http_client)
        self.relationships = RelationshipsAPI(self._http_client)

    @classmethod
    def from_env(cls, **overrides) -> "MOAClient":
        """Create client from environment variables.

        Environment variables:
        - MOA_API_KEY: API key (required)
        - MOA_ENVIRONMENT: Environment (alpha, beta, production)
        - MOA_API_VERSION: API version
        - MOA_TIMEOUT: Request timeout
        - MOA_MAX_RETRIES: Maximum retries
        - MOA_RETRY_DELAY: Retry delay
        - MOA_DEBUG: Debug mode

        Args:
            **overrides: Override any configuration values

        Returns:
            MOAClient: Configured client instance
        """
        return cls(**overrides)

    @classmethod
    def for_environment(
        cls, environment: Union[Environment, str], api_key: str, **kwargs
    ) -> "MOAClient":
        """Create client for specific environment.

        Args:
            environment: Target environment
            api_key: API key
            **kwargs: Additional configuration

        Returns:
            MOAClient: Configured client instance
        """
        return cls(api_key=api_key, environment=environment, **kwargs)

    @classmethod
    def for_alpha(cls, api_key: str, **kwargs) -> "MOAClient":
        """Create client for alpha environment."""
        return cls.for_environment(Environment.ALPHA, api_key, **kwargs)

    @classmethod
    def for_beta(cls, api_key: str, **kwargs) -> "MOAClient":
        """Create client for beta environment."""
        return cls.for_environment(Environment.BETA, api_key, **kwargs)

    @classmethod
    def for_production(cls, api_key: str, **kwargs) -> "MOAClient":
        """Create client for production environment."""
        return cls.for_environment(Environment.PRODUCTION, api_key, **kwargs)

    def health_check(self) -> HealthResponse:
        """Check API health status.

        Returns:
            HealthResponse: Health check result
        """
        # Use the base URL without API version for health check
        base_url = self.config.base_url
        response_data = self._http_client.get(f"{base_url}/health")
        return HealthResponse(**response_data)

    async def ahealth_check(self) -> HealthResponse:
        """Async check API health status."""
        base_url = self.config.base_url
        response_data = await self._http_client.aget(f"{base_url}/health")
        return HealthResponse(**response_data)

    def get_api_info(self) -> Dict[str, Any]:
        """Get API information.

        Returns:
            Dict containing API information
        """
        # Use the base URL without API version for root endpoint
        base_url = self.config.base_url
        return self._http_client.get(f"{base_url}/")

    async def aget_api_info(self) -> Dict[str, Any]:
        """Async get API information."""
        base_url = self.config.base_url
        return await self._http_client.aget(f"{base_url}/")

    def close(self) -> None:
        """Close the client and cleanup resources."""
        self._http_client.close()

    async def aclose(self) -> None:
        """Async close the client and cleanup resources."""
        await self._http_client.aclose()

    def __enter__(self) -> "MOAClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()

    async def __aenter__(self) -> "MOAClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.aclose()

    @property
    def environment(self) -> Environment:
        """Get current environment."""
        return self.config.environment

    @property
    def api_version(self) -> str:
        """Get current API version."""
        return self.config.api_version

    @property
    def base_url(self) -> str:
        """Get base URL."""
        return self.config.base_url

    @property
    def api_base_url(self) -> str:
        """Get API base URL with version."""
        return self.config.api_base_url

    def __repr__(self) -> str:
        """String representation of the client."""
        return (
            f"MOAClient(environment={self.environment.value}, "
            f"api_version={self.api_version}, "
            f"base_url={self.base_url})"
        )
