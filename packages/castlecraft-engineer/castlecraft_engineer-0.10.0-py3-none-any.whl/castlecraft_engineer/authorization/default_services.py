"""Module for default authorization service implementations."""

from typing import Any, Dict, List, Optional  # Dict moved for consistent ordering

from castlecraft_engineer.authorization.base_service import (
    AuthorizationError,
    AuthorizationService,
)
from castlecraft_engineer.authorization.permission import Permission


class DenyAllAuthorizationService(AuthorizationService):
    """An authorization service that always denies access."""

    async def check_permission(
        self,
        subject_id: Optional[str],
        required_permissions: List[Permission],
        provided_permissions: Optional[List[str]] = None,  # Corrected type
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Always denies the request by raising an AuthorizationError."""
        raise AuthorizationError(
            subject_id,
            required_permissions,
            "Access denied by DenyAll policy.",
        )


class AllowAllAuthorizationService(AuthorizationService):
    """An authorization service that always allows access."""

    async def check_permission(
        self,
        subject_id: Optional[str],
        required_permissions: List[Permission],
        provided_permissions: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Always allows the request."""
        return True
