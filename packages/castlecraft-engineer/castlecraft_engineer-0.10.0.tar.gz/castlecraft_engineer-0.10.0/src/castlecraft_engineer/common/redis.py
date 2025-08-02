from typing import Optional

import redis.asyncio as aredis
from redis import Redis
from redis.sentinel import Sentinel

from castlecraft_engineer.common.utils import split_string


def get_redis_connection(
    redis_uri: Optional[str] = None,
    is_sentinel_enabled: bool = False,
    sentinels_uri: Optional[str] = None,
    sentinel_username: Optional[str] = None,
    sentinel_password: Optional[str] = None,
    sentinel_master_username: Optional[str] = None,
    sentinel_master_password: Optional[str] = None,
    sentinel_master_service: Optional[str] = None,
):
    if is_sentinel_enabled:
        if not sentinels_uri:
            raise ValueError(
                "sentinels_uri must be provided when is_sentinel_enabled is True."
            )
        if not sentinel_master_service:
            raise ValueError(
                "sentinel_master_service must be provided when is_sentinel_enabled is True."
            )

        uris = split_string(",", sentinels_uri)
        sentinels = []
        for sen in uris:
            if ":" in sen:
                hostname, port = sen.split(":")
                try:
                    sentinels.append((hostname.strip(), int(port.strip())))
                except ValueError:
                    pass

        sentinel_kwargs = {}

        if sentinel_username:
            sentinel_kwargs["username"] = sentinel_username

        if sentinel_password:
            sentinel_kwargs["password"] = sentinel_password

        sentinel = Sentinel(
            sentinels=sentinels,
            sentinel_kwargs=sentinel_kwargs,
            username=sentinel_master_username,
            password=sentinel_master_password,
        )

        connection = sentinel.master_for(sentinel_master_service)
        connection.ping()
        return connection

    connection = Redis.from_url(redis_uri)
    connection.ping()
    return connection


async def get_async_redis_connection(
    redis_uri: Optional[str] = None,
    is_sentinel_enabled: bool = False,
    sentinels_uri: Optional[str] = None,
    sentinel_username: Optional[str] = None,
    sentinel_password: Optional[str] = None,
    sentinel_master_username: Optional[str] = None,
    sentinel_master_password: Optional[str] = None,
    sentinel_master_service: Optional[str] = None,
) -> aredis.Redis:
    """Gets an asynchronous Redis connection."""
    if is_sentinel_enabled:
        if not sentinels_uri:
            raise ValueError(
                "sentinels_uri must be provided when is_sentinel_enabled is True."
            )
        if not sentinel_master_service:
            raise ValueError(
                "sentinel_master_service must be provided when is_sentinel_enabled is True."
            )

        uris = split_string(",", sentinels_uri)
        sentinels = []
        for sen in uris:
            if ":" in sen:
                hostname, port_str = sen.split(":", 1)
                try:
                    sentinels.append((hostname.strip(), int(port_str.strip())))
                except ValueError:
                    pass

        sentinel_kwargs = {}
        if sentinel_username:
            sentinel_kwargs["username"] = sentinel_username
        if sentinel_password:
            sentinel_kwargs["password"] = sentinel_password

        sentinel = aredis.Sentinel(
            sentinels=sentinels,
            sentinel_kwargs=sentinel_kwargs,
            username=sentinel_master_username,
            password=sentinel_master_password,
        )

        connection = sentinel.master_for(sentinel_master_service)
        await connection.ping()

        return connection

    # Note: decode_responses=True can be added here if needed globally
    connection = aredis.from_url(redis_uri)
    # Use await for async ping
    await connection.ping()

    return connection
