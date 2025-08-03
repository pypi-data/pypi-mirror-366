"""Type definitions for Phlow authentication."""

from typing import Any

from pydantic import BaseModel, Field
from typing_extensions import TypedDict

try:
    from a2a.client import A2AClient
    from a2a.types import AgentCard as A2AAgentCard
except ImportError:
    A2AClient = None  # type: ignore
    A2AAgentCard = None  # type: ignore


# AgentCard type definition (A2A-compliant with Phlow extensions)
class AgentCard(BaseModel):
    """A2A-compliant Agent Card with Phlow-specific fields."""

    # A2A standard fields
    schema_version: str = "1.0"
    name: str
    description: str = ""
    service_url: str = ""
    skills: list[str] = []
    security_schemes: dict[str, Any] = {}
    metadata: dict[str, Any] | None = None

    # Phlow-specific fields (for backward compatibility)
    agent_id: str | None = None
    permissions: list[str] = []
    public_key: str | None = None
    endpoints: dict[str, Any] | None = None


class RateLimitingConfig(TypedDict):
    """Rate limiting configuration."""

    max_requests: int
    window_ms: int


class RateLimitConfigs(BaseModel):
    """Configuration for different types of rate limiting."""

    # Authentication rate limiting (per token hash)
    auth_max_requests: int = 60
    auth_window_ms: int = 60_000  # 1 minute

    # Role request rate limiting (per agent ID)
    role_request_max_requests: int = 10
    role_request_window_ms: int = 60_000  # 1 minute

    # Global rate limiting (all requests)
    global_max_requests: int | None = None
    global_window_ms: int = 60_000  # 1 minute


class PhlowConfig(BaseModel):
    """Phlow configuration."""

    # Supabase configuration
    supabase_url: str
    supabase_anon_key: str

    # Agent configuration (A2A-compliant)
    agent_card: AgentCard
    private_key: str
    public_key: str | None = None

    # Phlow-specific options
    enable_audit_log: bool = False
    enable_rate_limiting: bool = False
    rate_limit_config: RateLimitingConfig | None = (
        None  # Legacy, kept for compatibility
    )
    rate_limit_configs: RateLimitConfigs = Field(default_factory=RateLimitConfigs)


class PhlowContext(BaseModel):
    """Authentication context with Phlow extensions."""

    # From A2A authentication
    agent: AgentCard
    token: str
    claims: dict[str, Any]

    # Phlow additions
    supabase: Any  # SupabaseClient in production, mockable for tests
    a2a_client: Any | None = None  # A2AClient when available
    verified_roles: list[str] = Field(default_factory=list)  # RBAC verified roles

    model_config = {"arbitrary_types_allowed": True}


class VerifyOptions(BaseModel):
    """Options for token verification (kept for backward compatibility)."""

    required_permissions: list[str] | None = None
    allow_expired: bool = False


# Supabase-specific types
class SupabaseAgentRecord(TypedDict):
    """Agent record in Supabase."""

    agent_id: str
    name: str
    description: str | None
    service_url: str | None
    schema_version: str
    skills: list[dict[str, Any]]
    security_schemes: dict[str, Any]
    public_key: str
    metadata: dict[str, Any] | None
    created_at: str
    updated_at: str | None


class AuthAuditLog(TypedDict):
    """Authentication audit log entry."""

    id: str | None
    agent_id: str
    timestamp: str
    event_type: str  # 'authentication', 'authorization', 'rate_limit'
    success: bool
    metadata: dict[str, Any] | None
    error_code: str | None
    error_message: str | None


class AuditLog(BaseModel):
    """Audit log entry (kept for backward compatibility)."""

    timestamp: str
    event: str
    agent_id: str
    target_agent_id: str | None = None
    details: dict[str, Any] | None = None
