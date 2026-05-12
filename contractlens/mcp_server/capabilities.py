"""Detect MCP SDK features used by ContractLens (inspect / demos)."""

from __future__ import annotations


def sdk_installed() -> bool:
    try:
        import mcp.types  # noqa: F401
        from mcp.server import Server  # noqa: F401

        return True
    except Exception:
        return False


def sdk_supports_resources_and_prompts() -> bool:
    """True when Server exposes resource/prompt handlers (modern MCP Python SDK)."""
    try:
        from mcp.server import Server

        s = Server("contractlens-cap-probe")
        return all(
            callable(getattr(s, name))
            for name in ("list_resources", "read_resource", "list_prompts", "get_prompt")
        )
    except Exception:
        return False


def native_resources_prompts_available() -> bool:
    """True when handlers can be attached (SDK + probe registration on a throwaway Server)."""
    if not sdk_installed() or not sdk_supports_resources_and_prompts():
        return False
    from contractlens.mcp_server.server import probe_sdk_registration_ok

    return probe_sdk_registration_ok()


def server_mode_label() -> str:
    return "SDK registration active" if native_resources_prompts_available() else "fallback registry mode"
