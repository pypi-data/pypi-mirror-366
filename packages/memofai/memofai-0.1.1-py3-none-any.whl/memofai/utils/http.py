"""HTTP utilities for MOA SDK."""

import asyncio
import time
from typing import Any, Dict, Optional

from ..config import Config
from ..exceptions import (
    MOAAPIError,
    MOAAuthError,
    MOAConnectionError,
    MOANotFoundError,
    MOARateLimitError,
    MOAServerError,
    MOATimeoutError,
    MOAValidationError,
)

try:
    import httpx
except ImportError:
    # Fallback for when httpx is not installed during development
    httpx = None


class HTTPClient:
    """HTTP client for MOA API requests."""

    def __init__(self, config: Config):
        """Initialize HTTP client with configuration."""
        self.config = config
        self._client: Optional[Any] = None
        self._async_client: Optional[Any] = None

    @property
    def client(self) -> Any:
        """Get synchronous HTTP client."""
        if httpx is None:
            raise ImportError("httpx is required for HTTP requests")

        if self._client is None:
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
                "User-Agent": self.config.user_agent
                or f"memofai/{self._get_version()}",
            }

            self._client = httpx.Client(
                base_url=self.config.api_base_url,
                headers=headers,
                timeout=self.config.timeout,
            )

        return self._client

    @property
    def async_client(self) -> Any:
        """Get asynchronous HTTP client."""
        if httpx is None:
            raise ImportError("httpx is required for HTTP requests")

        if self._async_client is None:
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
                "User-Agent": self.config.user_agent
                or f"memofai/{self._get_version()}",
            }

            self._async_client = httpx.AsyncClient(
                base_url=self.config.api_base_url,
                headers=headers,
                timeout=self.config.timeout,
            )

        return self._async_client

    def _get_version(self) -> str:
        """Get SDK version."""
        try:
            from .. import __version__

            return __version__
        except ImportError:
            return "unknown"

    def close(self) -> None:
        """Close synchronous client."""
        if self._client:
            self._client.close()
            self._client = None

    async def aclose(self) -> None:
        """Close asynchronous client."""
        if self._async_client:
            await self._async_client.aclose()
            self._async_client = None

    def request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Make a synchronous HTTP request with retry logic."""
        for attempt in range(self.config.max_retries + 1):
            try:
                response = self.client.request(
                    method=method, url=url, params=params, json=json_data, **kwargs
                )
                return self._handle_response(response)

            except Exception as e:
                if attempt == self.config.max_retries:
                    raise self._handle_exception(e) from e

                # Wait before retry
                time.sleep(self.config.retry_delay * (2**attempt))

    async def arequest(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Make an asynchronous HTTP request with retry logic."""
        for attempt in range(self.config.max_retries + 1):
            try:
                response = await self.async_client.request(
                    method=method, url=url, params=params, json=json_data, **kwargs
                )
                return self._handle_response(response)

            except Exception as e:
                if attempt == self.config.max_retries:
                    raise self._handle_exception(e) from e

                # Wait before retry
                await asyncio.sleep(self.config.retry_delay * (2**attempt))

    def _handle_response(self, response: Any) -> Dict[str, Any]:
        """Handle HTTP response and convert errors."""
        if httpx is None:
            raise ImportError("httpx is required for HTTP requests")

        # Log response if debug mode is enabled
        if self.config.debug:
            print(f"Response: {response.status_code} {response.text}")

        # Handle different status codes
        if response.status_code == 200:
            try:
                return response.json()
            except ValueError:
                return {"data": response.text}

        elif response.status_code == 401:
            raise MOAAuthError("Authentication failed - check your API key")

        elif response.status_code == 404:
            raise MOANotFoundError("Resource not found")

        elif response.status_code == 422:
            try:
                error_data = response.json()
                raise MOAValidationError("Validation error", details=error_data)
            except ValueError as e:
                raise MOAValidationError("Validation error") from e

        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise MOARateLimitError(
                "Rate limit exceeded",
                retry_after=int(retry_after) if retry_after else None,
            )

        elif response.status_code >= 500:
            raise MOAServerError(
                f"Server error: {response.status_code}",
                status_code=response.status_code,
            )

        else:
            try:
                error_data = response.json()
                message = error_data.get("message", f"HTTP {response.status_code}")
            except ValueError:
                message = f"HTTP {response.status_code}: {response.text}"

            raise MOAAPIError(
                message,
                status_code=response.status_code,
                response_data=error_data if "error_data" in locals() else {},
            )

    def _handle_exception(self, exception: Exception) -> Exception:
        """Convert various exceptions to appropriate MOA exceptions."""
        if httpx is None:
            raise ImportError("httpx is required for HTTP requests")

        if isinstance(exception, httpx.TimeoutException):
            return MOATimeoutError(f"Request timeout: {exception}")

        elif isinstance(exception, httpx.ConnectError):
            return MOAConnectionError(f"Connection error: {exception}")

        elif isinstance(exception, httpx.RequestError):
            return MOAConnectionError(f"Request error: {exception}")

        else:
            return exception

    def get(
        self, url: str, params: Optional[Dict[str, Any]] = None, **kwargs
    ) -> Dict[str, Any]:
        """Make a GET request."""
        return self.request("GET", url, params=params, **kwargs)

    def post(
        self, url: str, json_data: Optional[Dict[str, Any]] = None, **kwargs
    ) -> Dict[str, Any]:
        """Make a POST request."""
        return self.request("POST", url, json_data=json_data, **kwargs)

    def put(
        self, url: str, json_data: Optional[Dict[str, Any]] = None, **kwargs
    ) -> Dict[str, Any]:
        """Make a PUT request."""
        return self.request("PUT", url, json_data=json_data, **kwargs)

    def delete(self, url: str, **kwargs) -> Dict[str, Any]:
        """Make a DELETE request."""
        return self.request("DELETE", url, **kwargs)

    async def aget(
        self, url: str, params: Optional[Dict[str, Any]] = None, **kwargs
    ) -> Dict[str, Any]:
        """Make an async GET request."""
        return await self.arequest("GET", url, params=params, **kwargs)

    async def apost(
        self, url: str, json_data: Optional[Dict[str, Any]] = None, **kwargs
    ) -> Dict[str, Any]:
        """Make an async POST request."""
        return await self.arequest("POST", url, json_data=json_data, **kwargs)

    async def aput(
        self, url: str, json_data: Optional[Dict[str, Any]] = None, **kwargs
    ) -> Dict[str, Any]:
        """Make an async PUT request."""
        return await self.arequest("PUT", url, json_data=json_data, **kwargs)

    async def adelete(self, url: str, **kwargs) -> Dict[str, Any]:
        """Make an async DELETE request."""
        return await self.arequest("DELETE", url, **kwargs)
