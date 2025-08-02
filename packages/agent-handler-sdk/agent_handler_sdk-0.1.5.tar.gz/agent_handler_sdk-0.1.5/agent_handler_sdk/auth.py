# agent_handler_sdk/auth.py

from typing import Optional


class AuthContext:
    """
    Auth context for tool execution that provides secure access to secrets.

    This class provides an isolated container for secrets during tool execution.
    Each tool execution should receive its own instance.
    """

    def __init__(self, secrets: Optional[dict[str, str]] = None, oauth2_token: Optional[str] = None):
        self._secrets = secrets or {}
        self._oauth2_token = oauth2_token

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a secret value by key"""
        return self._secrets.get(key, default)

    def get_oauth2_token(self) -> Optional[str]:
        """Get the OAuth token from the secrets"""
        return self._oauth2_token
