from dataclasses import dataclass
from functools import wraps
from typing import List, Optional, Union

from castlecraft_engineer.authorization.types import BaseStringEnum


@dataclass(frozen=True)
class Permission:
    action: BaseStringEnum
    resource: BaseStringEnum
    scope: Optional[BaseStringEnum] = None


def ctx(required_permissions: Union[Permission, List[Permission]]):
    """
    Decorator to associate required permission context(s)
    with a handler method.

    Injects 'required_permissions' (always as a list)
    into the keyword arguments passed to the decorated method,
    allowing the method's implementation to access it and
    perform authorization checks if needed.

    Args:
        required_permissions:
            A single Permission object or a list of Permissions.
    """

    perms_list = (
        [required_permissions]
        if isinstance(required_permissions, Permission)
        else required_permissions
    )

    def decorator(func):
        @wraps(func)
        def wrapper(handler_instance, *args, **kwargs):

            kwargs["required_permissions"] = perms_list

            return func(handler_instance, *args, **kwargs)

        return wrapper

    return decorator


# Example:
# class SomeCommandHandler(CommandHandler[SomeCommand]):

#     # Apply the decorator to associate the permission context
#     # @ctx(Permission(action='update', resource='widget'))
#     @ctx([
#         Permission(action='delete', resource='widget'),
#         Permission(action='notify', resource='admin')
#     ])
#     def execute(
#         self,
#         command: SomeCommand,
#         subject_id=None,
#         permissions=None,
#         **kwargs,

#     ):
#         required: Optional[Permission] = kwargs.get('required_permissions')

#         if required:
#             self._check_permission_logic(subject_id, permissions, required)

#         print(f"Handling command: {command} for subject: {subject_id}")

#     def _check_permission_logic(
#         self,
#         subject_id,
#         provided_permissions,
#         required_permission,
#     ):
#         print(
#             f"Checking if {subject_id} has {required_permission}"
#         )
#         # Replace with your actual permission checking logic
#         if not provided_permissions:
#             return False
#         return required_permission in provided_permissions
