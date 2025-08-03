"""Basic tests for Phlow authentication."""

from phlow.exceptions import PhlowError, TokenError
from phlow.types import AgentCard, PhlowConfig


def test_agent_card_creation():
    """Test agent card creation."""
    card = AgentCard(
        name="Test Agent",
        metadata={"agent_id": "test-agent", "public_key": "test-public-key"},
    )

    assert card.name == "Test Agent"
    assert card.metadata["agent_id"] == "test-agent"
    assert card.metadata["public_key"] == "test-public-key"
    assert card.skills == []


def test_phlow_config_creation():
    """Test Phlow config creation."""
    agent_card = AgentCard(
        name="Test Agent",
        metadata={"agent_id": "test-agent", "public_key": "test-public-key"},
    )

    config = PhlowConfig(
        supabase_url="https://test.supabase.co",
        supabase_anon_key="test-anon-key",
        agent_card=agent_card,
        private_key="test-private-key",
    )

    assert config.supabase_url == "https://test.supabase.co"
    assert config.supabase_anon_key == "test-anon-key"
    assert config.agent_card == agent_card
    assert config.private_key == "test-private-key"


def test_exception_hierarchy():
    """Test exception hierarchy."""
    # Test base exception
    error = PhlowError("test message")
    assert str(error) == "test message"
    assert error.status_code == 500

    # Test token error
    token_error = TokenError("token error")
    assert str(token_error) == "token error"
    assert token_error.status_code == 401
    assert isinstance(token_error, PhlowError)


def test_imports():
    """Test that main exports are available."""
    from phlow import (
        AgentCard,
        PhlowConfig,
        PhlowError,
        PhlowMiddleware,
        TokenError,
        generate_token,
        verify_token,
    )

    # Just check they're importable
    assert PhlowMiddleware is not None
    assert generate_token is not None
    assert verify_token is not None
    assert AgentCard is not None
    assert PhlowConfig is not None
    assert PhlowError is not None
    assert TokenError is not None
