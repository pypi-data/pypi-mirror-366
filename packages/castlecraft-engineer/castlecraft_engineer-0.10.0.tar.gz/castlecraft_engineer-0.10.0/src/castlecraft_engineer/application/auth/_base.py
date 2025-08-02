import logging
import types
from typing import TYPE_CHECKING, Any, Optional, Type

if TYPE_CHECKING:
    import redis  # pragma: no cover
    import redis.asyncio as aredis  # pragma: no cover

    _RedisClientForHint = redis.Redis  # pragma: no cover
    _AsyncRedisClientForHint = aredis.Redis  # pragma: no cover
else:
    _RedisClientForHint = Any
    _AsyncRedisClientForHint = Any

redis_module: Optional[types.ModuleType] = None
aredis_module: Optional[types.ModuleType] = None
RedisBaseError: Type[Exception] = Exception

try:
    import redis

    redis_module = redis
    RedisBaseError = redis.exceptions.RedisError
except ImportError:
    logging.getLogger(__name__).info(
        "Python 'redis' library not found. Synchronous caching will be disabled."
    )
try:
    import redis.asyncio as aredis

    aredis_module = aredis
except ImportError:
    logging.getLogger(__name__).info(
        "Python 'redis[asyncio]' library not found. Asynchronous caching will be disabled."
    )


class AuthenticationServiceBase:
    """
    Base class for AuthenticationService, declaring attributes
    expected by various mixin components.
    """

    _logger: logging.Logger
    _cache: Optional[_RedisClientForHint]
    _async_cache: Optional[_AsyncRedisClientForHint]  # This will be the resolved client
    _request_verify_ssl: bool

    # Configuration attributes (initialized in the main service class)
    JWKS_TTL_SEC: int
    DEFAULT_TOKEN_TTL_SEC: int
    ENABLE_BACKCHANNEL_LOGOUT: bool
    ENABLE_LOGOUT_BY_SUB: bool
    BACKCHANNEL_SID_MAP_TTL_SEC: int
    BACKCHANNEL_LOGOUT_TOKEN_ISS: Optional[str]
    BACKCHANNEL_LOGOUT_TOKEN_AUD: Optional[list[str] | str]
    BACKCHANNEL_SUB_MAP_TTL_SEC: int
