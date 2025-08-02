import pickle
from typing import Any, Optional

from ._base import AuthenticationServiceBase, RedisBaseError


class CacheMixin(AuthenticationServiceBase):
    def _get_cached_value(self, key: str) -> Optional[Any]:
        """
        Safely gets and deserializes a value from the sync cache.
        """
        if not self._cache:
            self._logger.debug("Cache client is not available.")
            return None
        try:
            val_bytes = self._cache.get(key)
            if not val_bytes:
                return None
            return pickle.loads(val_bytes)  # type: ignore[arg-type] # nosec
        except pickle.UnpicklingError as e:
            self._logger.warning(
                f"Failed to deserialize cached value for key '{key}': {e}"
            )
            return None
        except RedisBaseError as e:
            self._logger.error(f"Redis error while getting key '{key}': {e}")
            return None
        except Exception as e:
            self._logger.error(
                f"Unexpected error getting cache key '{key}': {e}",
                exc_info=True,
            )
            return None

    async def _get_cached_value_async(self, key: str) -> Optional[Any]:
        """Safely gets a value from the async cache."""
        async_cache_client = await self._get_resolved_async_cache_client()  # type: ignore
        if not async_cache_client:
            self._logger.debug(
                f"Async cache not available for get operation on key '{key}'."
            )
            return None
        try:
            val_bytes = await async_cache_client.get(key)
            if val_bytes:
                return pickle.loads(val_bytes)  # type: ignore[arg-type] # nosec
            else:
                return None
        except (
            RedisBaseError,
            ConnectionRefusedError,
            TypeError,
            EOFError,
            pickle.UnpicklingError,
        ) as e:
            self._logger.warning(
                f"Async cache get/deserialize error for key '{key}': {e}"
            )
            return None

    def _set_cached_value(self, key: str, value: Any, ttl: Optional[int]):
        """Safely sets a value in the sync cache."""
        if not self._cache:
            self._logger.debug(
                f"Cache not available for set operation on key '{key}'.",
            )
            return
        try:
            self._cache.set(key, pickle.dumps(value), ex=ttl)
        except (
            RedisBaseError,
            ConnectionRefusedError,
            TypeError,
            pickle.PicklingError,
        ) as e:
            self._logger.warning(f"Sync cache set error for key '{key}': {e}")

    async def _set_cached_value_async(self, key: str, value: Any, ttl: Optional[int]):
        """Safely sets a value in the async cache."""
        async_cache_client = await self._get_resolved_async_cache_client()  # type: ignore
        if not async_cache_client:
            self._logger.debug(
                f"Async cache not available for set operation on key '{key}'."
            )
            return
        try:
            await async_cache_client.set(key, pickle.dumps(value), ex=ttl)
        except (
            RedisBaseError,
            ConnectionRefusedError,
            TypeError,
            pickle.PicklingError,
        ) as e:
            self._logger.warning(f"Async cache set error for key '{key}': {e}")

    def _delete_cached_value(self, key: str):
        """Safely deletes a value from the sync cache."""
        if not self._cache:
            self._logger.debug(
                f"Cache not available for delete operation on key '{key}'."
            )
            return
        try:
            self._cache.delete(key)
        except (RedisBaseError, ConnectionRefusedError) as e:
            self._logger.warning(f"Sync cache delete error for key '{key}': {e}")

    async def _delete_cached_value_async(self, key: str):
        """Safely deletes a value from the async cache."""
        async_cache_client = await self._get_resolved_async_cache_client()  # type: ignore
        if not async_cache_client:
            self._logger.debug(
                f"Async cache not available for delete operation on key '{key}'."
            )
            return
        try:
            await async_cache_client.delete(key)
        except (RedisBaseError, ConnectionRefusedError) as e:
            self._logger.warning(f"Async cache delete error for key '{key}': {e}")
