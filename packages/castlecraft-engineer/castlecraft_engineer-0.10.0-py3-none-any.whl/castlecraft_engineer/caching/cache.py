import logging
from os import environ
from typing import Optional

from redis.exceptions import ConnectionError

from castlecraft_engineer.common.env import (
    DEFAULT_CACHE_REDIS_URL,
    ENV_CACHE_REDIS_MASTER_PASSWORD,
    ENV_CACHE_REDIS_MASTER_SERVICE,
    ENV_CACHE_REDIS_MASTER_USERNAME,
    ENV_CACHE_REDIS_SENTINEL_PASSWORD,
    ENV_CACHE_REDIS_SENTINEL_USERNAME,
    ENV_CACHE_REDIS_SENTINELS,
    ENV_CACHE_REDIS_URL,
    ENV_ENABLE_CACHE_REDIS_CLUSTER,
)
from castlecraft_engineer.common.redis import (
    get_async_redis_connection,
    get_redis_connection,
)

logger = logging.getLogger(__name__)


def _is_truthy(value: Optional[str]) -> bool:
    """Checks if a string value represents a truthy value."""
    if value is None:
        return False
    return value.lower() in ("true", "1", "yes", "on")


def get_redis_cache_connection(
    redis_uri: Optional[str] = None,
    is_sentinel_enabled: Optional[bool] = None,
    sentinels_uri: Optional[str] = None,
    sentinel_username: Optional[str] = None,
    sentinel_password: Optional[str] = None,
    sentinel_master_username: Optional[str] = None,
    sentinel_master_password: Optional[str] = None,
    sentinel_master_service: Optional[str] = None,
):
    """
    Gets a synchronous Redis connection, allowing programmatic overrides.
    Falls back to environment variables if parameters are not provided.
    """
    try:
        # Prioritize programmatic parameters, then fall back to environment variables
        final_redis_uri = (
            redis_uri
            if redis_uri is not None
            else environ.get(ENV_CACHE_REDIS_URL, DEFAULT_CACHE_REDIS_URL)
        )
        final_is_sentinel_enabled = (
            is_sentinel_enabled
            if is_sentinel_enabled is not None
            else _is_truthy(environ.get(ENV_ENABLE_CACHE_REDIS_CLUSTER))
        )
        final_sentinels_uri = (
            sentinels_uri
            if sentinels_uri is not None
            else environ.get(ENV_CACHE_REDIS_SENTINELS)
        )
        final_sentinel_username = (
            sentinel_username
            if sentinel_username is not None
            else environ.get(ENV_CACHE_REDIS_SENTINEL_USERNAME)
        )
        final_sentinel_password = (
            sentinel_password
            if sentinel_password is not None
            else environ.get(ENV_CACHE_REDIS_SENTINEL_PASSWORD)
        )
        final_master_username = (
            sentinel_master_username
            if sentinel_master_username is not None
            else environ.get(ENV_CACHE_REDIS_MASTER_USERNAME)
        )
        final_master_password = (
            sentinel_master_password
            if sentinel_master_password is not None
            else environ.get(ENV_CACHE_REDIS_MASTER_PASSWORD)
        )
        final_master_service = (
            sentinel_master_service
            if sentinel_master_service is not None
            else environ.get(ENV_CACHE_REDIS_MASTER_SERVICE)
        )

        return get_redis_connection(
            redis_uri=final_redis_uri,
            is_sentinel_enabled=final_is_sentinel_enabled,
            sentinels_uri=final_sentinels_uri,
            sentinel_username=final_sentinel_username,
            sentinel_password=final_sentinel_password,
            sentinel_master_username=final_master_username,
            sentinel_master_password=final_master_password,
            sentinel_master_service=final_master_service,
        )
    except ConnectionError as exc:
        logger.error(exc)
        return None


async def get_redis_cache_async_connection(
    redis_uri: Optional[str] = None,
    is_sentinel_enabled: Optional[bool] = None,
    sentinels_uri: Optional[str] = None,
    sentinel_username: Optional[str] = None,
    sentinel_password: Optional[str] = None,
    sentinel_master_username: Optional[str] = None,
    sentinel_master_password: Optional[str] = None,
    sentinel_master_service: Optional[str] = None,
):
    """
    Gets an asynchronous Redis connection, allowing programmatic overrides.
    Falls back to environment variables if parameters are not provided.
    """
    try:
        # Prioritize programmatic parameters, then fall back to environment variables
        final_redis_uri = (
            redis_uri
            if redis_uri is not None
            else environ.get(ENV_CACHE_REDIS_URL, DEFAULT_CACHE_REDIS_URL)
        )
        final_is_sentinel_enabled = (
            is_sentinel_enabled
            if is_sentinel_enabled is not None
            else _is_truthy(environ.get(ENV_ENABLE_CACHE_REDIS_CLUSTER))
        )
        final_sentinels_uri = (
            sentinels_uri
            if sentinels_uri is not None
            else environ.get(ENV_CACHE_REDIS_SENTINELS)
        )
        final_sentinel_username = (
            sentinel_username
            if sentinel_username is not None
            else environ.get(ENV_CACHE_REDIS_SENTINEL_USERNAME)
        )
        final_sentinel_password = (
            sentinel_password
            if sentinel_password is not None
            else environ.get(ENV_CACHE_REDIS_SENTINEL_PASSWORD)
        )
        final_master_username = (
            sentinel_master_username
            if sentinel_master_username is not None
            else environ.get(ENV_CACHE_REDIS_MASTER_USERNAME)
        )
        final_master_password = (
            sentinel_master_password
            if sentinel_master_password is not None
            else environ.get(ENV_CACHE_REDIS_MASTER_PASSWORD)
        )
        final_master_service = (
            sentinel_master_service
            if sentinel_master_service is not None
            else environ.get(ENV_CACHE_REDIS_MASTER_SERVICE)
        )

        return await get_async_redis_connection(
            redis_uri=final_redis_uri,
            is_sentinel_enabled=final_is_sentinel_enabled,
            sentinels_uri=final_sentinels_uri,
            sentinel_username=final_sentinel_username,
            sentinel_password=final_sentinel_password,
            sentinel_master_username=final_master_username,
            sentinel_master_password=final_master_password,
            sentinel_master_service=final_master_service,
        )
    except ConnectionError as exc:
        logger.error(exc)
        return None
