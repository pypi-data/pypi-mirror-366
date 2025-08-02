from typing import Any, Dict, List, Optional

from castlecraft_engineer.authorization.base_service import (
    AuthorizationError,
    AuthorizationService,
)
from castlecraft_engineer.authorization.permission import Permission


class MockAuthorizationService(AuthorizationService):
    """
    A test helper for AuthorizationService. Allows spying on calls
    and configuring behavior.
    """

    def __init__(self, allow: bool = True, raise_error_on_deny: bool = True):
        self.allow = allow
        self.raise_error_on_deny = raise_error_on_deny
        self.last_subject_id: Optional[str] = None
        self.last_required_permissions: Optional[List[Permission]] = None
        self.last_context: Optional[Dict[str, Any]] = None
        self.call_count = 0

    async def check_permission(
        self,
        subject_id: Optional[str],
        required_permissions: List[Permission],
        provided_permissions: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        self.call_count += 1
        self.last_subject_id = subject_id
        self.last_required_permissions = required_permissions
        self.last_context = context

        if self.allow:
            return True
        else:
            if self.raise_error_on_deny:
                raise AuthorizationError(
                    subject_id,
                    required_permissions,
                    "Access denied by mock policy.",
                )
            else:
                return False

    def reset(self):
        """Resets call history for reuse in tests."""
        self.last_subject_id = None
        self.last_required_permissions = None
        self.last_context = None
        self.call_count = 0
