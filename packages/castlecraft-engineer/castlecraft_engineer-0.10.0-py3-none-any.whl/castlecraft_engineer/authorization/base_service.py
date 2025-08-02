import abc
from typing import Any, Dict, List, Optional

from castlecraft_engineer.authorization.permission import Permission


class AuthorizationError(Exception):
    """Custom exception for authorization failures."""

    def __init__(
        self,
        subject_id: Optional[str],
        required_permissions: List[Permission],
        message: str = "Forbidden",
    ):
        self.subject_id = subject_id
        self.required_permissions = required_permissions
        super().__init__(
            f"Subject '{subject_id}' is not authorized for required "
            f"permissions: {required_permissions}. Reason: {message}"
        )


class AuthorizationService(abc.ABC):
    """
    Abstract interface for authorization checks.
    Implementations connect to engines like Casbin,
    OPA, SpiceDB, etc.
    """

    @abc.abstractmethod
    async def check_permission(
        self,
        subject_id: Optional[str],
        required_permissions: List[Permission],
        # Optional: Pass permissions/attributes associated with the subject
        # (e.g., from token claims like roles, groups, or other string-based attributes)
        # if the engine needs them directly for evaluation.
        provided_permissions: Optional[List[str]] = None,
        # Optional: Pass additional context relevant to the decision
        # (e.g., resource owner, tenant id, command/query data)
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Checks if the subject has the required permissions.

        Args:
            subject_id: Identifier of the user/service performing the action.
                        Can be None for anonymous
                        checks if supported by the policy.
            required_permissions: A list of Permission objects
                                  declared by the handler
                                  via the @ctx decorator.
            provided_permissions: Optional list of permissions
                                  the subject possesses.
            context: Optional dictionary containing additional
                     data for policy evaluation.

        Returns:
            True if authorized.

        Raises:
            AuthorizationError: If the check fails.
                                This is often preferred over
                                returning False to halt execution clearly.
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError


# Example Command Handler Usage
# class UpdateWidgetCommand(Command):
#     widget_id: int
#     new_name: str
#     # Add other relevant fields that might be needed for context
#     owner_id: str

# @command_bus.register
# class UpdateWidgetCommandHandler(CommandHandler[UpdateWidgetCommand]):

#     def __init__(self, auth_service: AuthorizationService, /* other deps */):
#         self._auth_service = auth_service
#         # ...

#     # Declare permission needed
#     @ctx(Permission(action='update', resource='widget'))
#     def execute(
#         self,
#         command: UpdateWidgetCommand,
#         subject_id: Optional[str] = None,
#         permissions: Optional[List[Dict[str, str]]] = None,
#         *args,
#         **kwargs,
#     ) -> Any:
#         # 1. Get required permissions from decorator
#         required: Optional[List[Permission]] = kwargs.get('required_permissions')  # noqa: E501

#         # 2. Prepare context (optional, depends on policy needs)
#         auth_context = {
#             "resource_id": command.widget_id,
#             "resource_owner": command.owner_id,
#             # Add any other relevant data from the command or environment
#         }

#         # 3. Perform the check using the injected service
#         if required:
#             # This will raise AuthorizationError if check fails
#             await self._auth_service.check_permission(
#                 subject_id=subject_id,
#                 required_permissions=required,
#                 provided_permissions=permissions,
#                 context=auth_context
#             )
#
#         # Proceed with command logic...
#         print(f"Executing UpdateWidgetCommand for {command.widget_id}")
#         # ... update widget in repository ...
#         return {"status": "updated", "widget_id": command.widget_id}
