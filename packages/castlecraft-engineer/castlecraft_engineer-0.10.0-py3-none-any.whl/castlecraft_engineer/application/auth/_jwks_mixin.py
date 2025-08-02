import os
from typing import Optional

from castlecraft_engineer.common.env import ENV_JWKS_URL
from castlecraft_engineer.common.requests import HTTPError, requests

from ._base import AuthenticationServiceBase
from ._constants import JWKS_RESPONSE_KEY  # Import constant


class JwksMixin(AuthenticationServiceBase):
    def _is_jwks_valid(self, jwks_data: dict) -> bool:
        """Validates the structure of JWKS data."""
        if (
            not isinstance(jwks_data, dict)
            or "keys" not in jwks_data
            or not isinstance(jwks_data["keys"], list)
        ):
            return False

        for key in jwks_data["keys"]:
            if not isinstance(key, dict) or "kty" not in key or "kid" not in key:
                return False
        return True

    async def get_active_jwks_response(self) -> Optional[dict]:
        """Fetches JWKS from cache or URL."""
        jwks_url = os.environ.get(ENV_JWKS_URL)
        if not jwks_url:
            self._logger.warning(
                f"{ENV_JWKS_URL} environment variable not set.",
            )
            return None

        async_cache_client = await self._get_resolved_async_cache_client()  # type: ignore
        if async_cache_client:
            jwks_response = await self._get_cached_value_async(JWKS_RESPONSE_KEY)  # type: ignore
        else:
            jwks_response = self._get_cached_value(JWKS_RESPONSE_KEY)  # type: ignore

        if jwks_response:
            if self._is_jwks_valid(jwks_response):
                return jwks_response
            else:
                self._logger.warning(
                    "Cached JWKS data is invalid. Fetching fresh.",
                )
                if async_cache_client:
                    await self._delete_cached_value_async(JWKS_RESPONSE_KEY)  # type: ignore
                else:
                    self._delete_cached_value(JWKS_RESPONSE_KEY)  # type: ignore

        self._logger.info(f"Fetching JWKS from URL: {jwks_url}")
        try:
            response = requests.get(
                jwks_url,
                timeout=10,
                verify=self._request_verify_ssl,
            )
            response.raise_for_status()
            jwks_response = response.json()
        except HTTPError as e:
            self._logger.error(
                f"HTTPError fetching JWKS from {jwks_url}: {e}", exc_info=True
            )
            return None
        except ValueError as e:  # For JSON decoding errors
            self._logger.error(
                f"ValueError decoding JWKS JSON from {jwks_url}: {e}", exc_info=True
            )
            return None

        if not self._is_jwks_valid(jwks_response):
            self._logger.error(f"Fetched JWKS data from {jwks_url} is invalid.")
            return None

        if async_cache_client:
            await self._set_cached_value_async(JWKS_RESPONSE_KEY, jwks_response, ttl=self.JWKS_TTL_SEC)  # type: ignore
        else:
            self._set_cached_value(JWKS_RESPONSE_KEY, jwks_response, ttl=self.JWKS_TTL_SEC)  # type: ignore
        return jwks_response
