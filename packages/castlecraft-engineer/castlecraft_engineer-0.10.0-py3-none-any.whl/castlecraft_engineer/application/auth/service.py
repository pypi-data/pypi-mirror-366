import asyncio
import inspect
import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

from castlecraft_engineer.common.env import (
    DEFAULT_AUTH_JWKS_TTL_SEC,
    DEFAULT_AUTH_TOKEN_TTL_SEC,
    DEFAULT_AUTHENTICATION_REQUEST_VERIFY_SSL,
    ENV_ALLOWED_AUD,
    ENV_AUTH_JWKS_TTL_SEC,
    ENV_AUTH_TOKEN_TTL_SEC,
    ENV_AUTHENTICATION_REQUEST_VERIFY_SSL,
    ENV_BACKCHANNEL_LOGOUT_TOKEN_ISS,
    ENV_BACKCHANNEL_SID_MAP_TTL_SEC,
    ENV_BACKCHANNEL_SUB_MAP_TTL_SEC,
    ENV_CLIENT_ID,
    ENV_ENABLE_BACKCHANNEL_LOGOUT,
    ENV_ENABLE_INTROSPECT_TOKEN,
    ENV_ENABLE_LOGOUT_BY_SUB,
    ENV_ENABLE_VERIFY_ID_TOKEN,
    ENV_INTROSPECT_URL,
    ENV_USERINFO_URL,
)
from castlecraft_engineer.common.utils import split_string  # noqa: E402

from ._base import (
    AuthenticationServiceBase,
    _AsyncRedisClientForHint,
    _RedisClientForHint,
)
from ._bcl_mixin import BackchannelLogoutMixin
from ._cache_mixin import CacheMixin
from ._constants import (
    BEARER_TOKEN_KEY_PREFIX,
    DEFAULT_BACKCHANNEL_SID_MAP_TTL_SEC,
    DEFAULT_BACKCHANNEL_SUB_MAP_TTL_SEC,
)
from ._jwks_mixin import JwksMixin
from ._verification_mixin import VerificationMixin


class AuthenticationService(
    CacheMixin,
    JwksMixin,
    VerificationMixin,
    BackchannelLogoutMixin,
    AuthenticationServiceBase,
):
    """
    Handles token verification, introspection,
    and user info fetching, using cache.
    """

    def __init__(
        self,
        cache_client: Optional[_RedisClientForHint] = None,
        async_cache_client: Optional[_AsyncRedisClientForHint] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._cache = cache_client
        self._async_cache = async_cache_client
        self._config = config or {}
        self._async_cache_resolve_lock = asyncio.Lock()

        def _get_config_value(key: str, env_var: str, default: Any) -> Any:
            """Gets a value from config, falling back to env, then default."""
            # Prioritize config dict, then environment, then default
            return self._config.get(key, os.environ.get(env_var, default))

        def _get_bool_config(key: str, env_var: str, default: str) -> bool:
            """Gets a boolean value from config, falling back to env, then default."""
            value = str(_get_config_value(key, env_var, default)).lower()
            return value in ("true", "1", "yes", "on")

        # --- General & Verification Config ---
        self._request_verify_ssl: bool = _get_bool_config(
            "request_verify_ssl",
            ENV_AUTHENTICATION_REQUEST_VERIFY_SSL,
            DEFAULT_AUTHENTICATION_REQUEST_VERIFY_SSL,
        )
        self.JWKS_TTL_SEC = int(
            _get_config_value(
                "jwks_ttl_sec", ENV_AUTH_JWKS_TTL_SEC, DEFAULT_AUTH_JWKS_TTL_SEC
            )
        )
        self.DEFAULT_TOKEN_TTL_SEC = int(
            _get_config_value(
                "default_token_ttl_sec",
                ENV_AUTH_TOKEN_TTL_SEC,
                DEFAULT_AUTH_TOKEN_TTL_SEC,
            )
        )
        self.ALLOWED_AUD = split_string(
            ",", _get_config_value("allowed_aud", ENV_ALLOWED_AUD, "")
        )

        # --- Introspection & UserInfo Config ---
        self.INTROSPECT_URL = _get_config_value(
            "introspect_url", ENV_INTROSPECT_URL, None
        )
        self.USERINFO_URL = _get_config_value("userinfo_url", ENV_USERINFO_URL, None)

        self.JWKS_TTL_SEC = int(
            os.environ.get(ENV_AUTH_JWKS_TTL_SEC, DEFAULT_AUTH_JWKS_TTL_SEC)
        )
        self.DEFAULT_TOKEN_TTL_SEC = int(
            os.environ.get(ENV_AUTH_TOKEN_TTL_SEC, DEFAULT_AUTH_TOKEN_TTL_SEC)
        )
        self._async_cache_resolve_lock = asyncio.Lock()

        # Backchannel Logout Configuration
        self.ENABLE_BACKCHANNEL_LOGOUT = (
            os.environ.get(ENV_ENABLE_BACKCHANNEL_LOGOUT, "false").lower() == "true"
        )
        # Enable logout by 'sub' only if backchannel logout is enabled
        self.ENABLE_LOGOUT_BY_SUB = (
            self.ENABLE_BACKCHANNEL_LOGOUT
            and os.environ.get(ENV_ENABLE_LOGOUT_BY_SUB, "false").lower() == "true"
        )

        # Backchannel Logout Cache TTLs
        self.BACKCHANNEL_SID_MAP_TTL_SEC = int(
            os.environ.get(
                ENV_BACKCHANNEL_SID_MAP_TTL_SEC, DEFAULT_BACKCHANNEL_SID_MAP_TTL_SEC
            )
        )  # Expected issuer for logout tokens
        self.BACKCHANNEL_LOGOUT_TOKEN_ISS = os.environ.get(
            ENV_BACKCHANNEL_LOGOUT_TOKEN_ISS
        )
        # For backchannel logout, the audience can be a list derived from ENV_ALLOWED_AUD,
        # or fallback to ENV_CLIENT_ID if ENV_ALLOWED_AUD is not set.
        # This allows logout tokens to be validated if they are intended for any of the
        # service's configured allowed audiences.
        allowed_audiences_str = os.environ.get(ENV_ALLOWED_AUD)
        if allowed_audiences_str:
            self.BACKCHANNEL_LOGOUT_TOKEN_AUD = split_string(",", allowed_audiences_str)
        else:
            # Fallback to client_id if ENV_ALLOWED_AUD is not set or empty
            self.BACKCHANNEL_LOGOUT_TOKEN_AUD = os.environ.get(ENV_CLIENT_ID)

        self.BACKCHANNEL_SUB_MAP_TTL_SEC = int(
            os.environ.get(
                ENV_BACKCHANNEL_SUB_MAP_TTL_SEC, DEFAULT_BACKCHANNEL_SUB_MAP_TTL_SEC
            )
        )

    async def _get_resolved_async_cache_client(
        self,
    ) -> Optional[_AsyncRedisClientForHint]:
        """
        Ensures self._async_cache is an actual client instance.
        If self._async_cache is an awaitable (coroutine), it awaits it to get
        the client instance and updates self._async_cache to store this instance
        for subsequent uses.
        """
        # Quick check if already resolved (no longer an awaitable)
        if self._async_cache is not None and not inspect.isawaitable(self._async_cache):
            return self._async_cache

        # If it's None or still an awaitable, proceed under lock
        async with self._async_cache_resolve_lock:
            # Double-check after acquiring lock, another task might have resolved it
            if self._async_cache is not None and not inspect.isawaitable(
                self._async_cache
            ):
                return self._async_cache

            # If it's still an awaitable (and not None), resolve it
            if self._async_cache is not None and inspect.isawaitable(self._async_cache):
                self._logger.debug(
                    "Original _async_cache is an awaitable. Awaiting to get client instance."
                )
                try:
                    resolved_client = await self._async_cache
                    # Update self._async_cache to the resolved client
                    self._async_cache = resolved_client
                    if not self._async_cache:
                        self._logger.warning(
                            "Awaiting the async cache coroutine resulted in None."
                        )
                except RuntimeError as e:
                    # Catch the specific error
                    if "coroutine is being awaited already" in str(e):
                        # This should ideally not happen if the lock is effective.
                        self._logger.error(
                            "Race condition: Async cache coroutine was already being awaited. "
                            "This might indicate an issue with concurrent initialization or a bug. "
                            f"Error: {e}",
                            exc_info=True,
                        )
                        # Mark as failed to prevent further errors
                        # with this specific coroutine object.
                        self._async_cache = None
                    else:
                        # Other RuntimeErrors
                        self._logger.error(
                            f"RuntimeError during async cache client resolution: {e}",
                            exc_info=True,
                        )
                        self._async_cache = None
                except Exception as e:
                    self._logger.error(
                        f"Failed to resolve awaitable async cache client: {e}",
                        exc_info=True,
                    )
                    self._async_cache = None
        return self._async_cache

    def is_token_valid(self, user: Optional[dict]) -> bool:
        """
        Checks if the user data from cache
        is still valid based on expiry.
        """

        if isinstance(user, dict) and user.get("exp", 0) > datetime.now().timestamp():
            self._logger.debug(
                "Cached token data for prefix"  # noqa: E501
                f" '{BEARER_TOKEN_KEY_PREFIX}' is valid."
            )
            return True
        if user:
            self._logger.info(
                "Cached token data for prefix "  # noqa: E501
                f"'{BEARER_TOKEN_KEY_PREFIX}' expired or invalid. Deleting."
            )
        return False

    async def verify_user(self, token: str) -> Optional[dict]:
        """
        Asynchronously verifies a user token by checking cache,
        then optionally ID token verification or token introspection.
        Verifies a user token by checking cache,
        then optionally ID token verification
        or token introspection.
        """
        if not token:
            self._logger.warning("verify_user called with empty token.")
            return None

        cache_key = BEARER_TOKEN_KEY_PREFIX + token
        async_cache_client = await self._get_resolved_async_cache_client()
        if async_cache_client:
            user = await self._get_cached_value_async(cache_key)
        else:
            user = self._get_cached_value(cache_key)

        if self.is_token_valid(user):
            return user
        elif user:
            # User payload was found in cache but is invalid/expired
            self._logger.info(f"Cached token {cache_key} is invalid/expired. Deleting.")
            # Attempt to unlink from SID map if backchannel logout is enabled
            if self.ENABLE_BACKCHANNEL_LOGOUT:
                sid = user.get("sid")  # user is the payload from cache
                if sid:
                    await self._unlink_sid_from_token(sid, cache_key)
            # Delete the main token cache entry
            # Note: Unlinking from SUB map happens when invalidating by SID/SUB
            if async_cache_client:
                await self._delete_cached_value_async(cache_key)
            else:
                self._delete_cached_value(cache_key)

        self._logger.info(
            "Token not found in cache or expired."  # noqa: E501
            "Attempting verification/introspection."
        )

        if (
            os.environ.get(
                ENV_ENABLE_VERIFY_ID_TOKEN,
                "false",
            ).lower()
            == "true"
        ):
            self._logger.debug(
                "Attempting ID token verification.",
            )
            user = await self.verify_id_token(token)
            if user:
                return user

        if (
            os.environ.get(
                ENV_ENABLE_INTROSPECT_TOKEN,
                "false",
            ).lower()
            == "true"
        ):
            self._logger.debug(
                "Attempting token introspection.",
            )
            user = await self.introspect_token(token)
            if user:
                return user

        self._logger.warning(
            f"Token verification failed for prefix '{BEARER_TOKEN_KEY_PREFIX}'."  # noqa: E501
        )
        return None
