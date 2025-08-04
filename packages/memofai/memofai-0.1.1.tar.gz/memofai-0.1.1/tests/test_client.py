"""Test client initialization and configuration."""

from unittest.mock import patch

from memofai import Config, Environment, MOAClient


def test_client_initialization_with_api_key():
    """Test client initialization with explicit API key."""
    client = MOAClient(
        api_key="test-key", environment=Environment.BETA, api_version="v1"
    )

    assert client.config.api_key == "test-key"
    assert client.config.environment == Environment.BETA
    assert client.config.api_version == "v1"
    assert client.environment == Environment.BETA
    assert client.api_version == "v1"


def test_client_environment_specific_constructors():
    """Test environment-specific client constructors."""
    api_key = "test-key"

    # Test alpha client
    alpha_client = MOAClient.for_alpha(api_key)
    assert alpha_client.environment == Environment.ALPHA

    # Test beta client
    beta_client = MOAClient.for_beta(api_key)
    assert beta_client.environment == Environment.BETA

    # Test production client
    prod_client = MOAClient.for_production(api_key)
    assert prod_client.environment == Environment.PRODUCTION


def test_client_from_env(mock_config_env):
    """Test client creation from environment variables."""
    client = MOAClient.from_env()

    assert client.config.api_key == "test-api-key-12345"
    assert client.config.environment == Environment.BETA


def test_client_context_manager():
    """Test client as context manager."""
    with patch.object(MOAClient, "close") as mock_close:
        with MOAClient(api_key="test-key") as client:
            assert isinstance(client, MOAClient)
        mock_close.assert_called_once()


def test_client_repr():
    """Test client string representation."""
    client = MOAClient(api_key="test-key", environment=Environment.BETA)
    repr_str = repr(client)

    assert "MOAClient" in repr_str
    assert "environment=beta" in repr_str
    assert "api_version=v1" in repr_str


def test_config_validation():
    """Test configuration validation."""
    # Test empty API key validation
    try:
        Config.from_env(api_key="")
        raise AssertionError("Should have raised ValueError")
    except ValueError as e:
        assert "API key is required" in str(e)

    # Test invalid environment
    try:
        Config.from_env(api_key="test", environment="invalid")
        raise AssertionError("Should have raised ValueError")
    except ValueError as e:
        assert "Invalid environment: invalid" in str(e)


def test_config_properties():
    """Test configuration properties."""
    config = Config.from_env(
        api_key="test-key", environment=Environment.BETA, api_version="v2"
    )

    assert config.base_url == "https://beta-api.memof.ai"
    assert config.api_base_url == "https://beta-api.memof.ai/api/v2/"

    # Test production URLs
    prod_config = Config.from_env(
        api_key="test-key", environment=Environment.PRODUCTION
    )

    assert prod_config.base_url == "https://api.memof.ai"
    assert prod_config.api_base_url == "https://api.memof.ai/api/v1/"


def test_timeout_validation():
    """Test timeout validation."""
    try:
        Config.from_env(api_key="test", timeout=-1)
        raise AssertionError("Should have raised ValueError")
    except ValueError as e:
        assert "Timeout must be positive" in str(e)


def test_max_retries_validation():
    """Test max retries validation."""
    try:
        Config.from_env(api_key="test", max_retries=-1)
        raise AssertionError("Should have raised ValueError")
    except ValueError as e:
        assert "Max retries cannot be negative" in str(e)


def test_client_api_access():
    """Test that client provides access to API modules."""
    client = MOAClient(api_key="test-key")

    # Check that API modules are accessible
    assert hasattr(client, "memory")
    assert hasattr(client, "graph")
    assert hasattr(client, "relationships")

    # Check API module types
    from memofai.api import GraphSearchAPI, MemoryAPI, RelationshipsAPI

    assert isinstance(client.memory, MemoryAPI)
    assert isinstance(client.graph, GraphSearchAPI)
    assert isinstance(client.relationships, RelationshipsAPI)
