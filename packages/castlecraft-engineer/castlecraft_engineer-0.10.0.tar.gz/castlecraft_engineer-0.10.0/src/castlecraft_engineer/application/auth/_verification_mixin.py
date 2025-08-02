import asyncio
import os
from datetime import datetime
from typing import Dict  # Add import
from typing import Optional

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey  # Add import
from jwt import decode, get_unverified_header  # decode is used here
from jwt.algorithms import RSAAlgorithm

from castlecraft_engineer.common.env import (
    DEFAULT_INTROSPECT_TOKEN_KEY,
    ENV_ALLOWED_AUD,
    ENV_CLIENT_ID,
    ENV_CLIENT_SECRET,
    ENV_ENABLE_FETCH_USERINFO,
    ENV_INTROSPECT_REQUIRES_AUTH,
    ENV_INTROSPECT_TOKEN_KEY,
    ENV_INTROSPECT_URL,
    ENV_USERINFO_URL,
)
from castlecraft_engineer.common.requests import HTTPError, requests
from castlecraft_engineer.common.utils import split_string

from ._base import AuthenticationServiceBase
from ._constants import BEARER_TOKEN_KEY_PREFIX  # Import constant


class VerificationMixin(AuthenticationServiceBase):
    async def verify_id_token(self, token: str) -> Optional[dict]:
        """Verifies an ID token using JWKS."""
        jwks_response = await self.get_active_jwks_response()  # type: ignore
        if not jwks_response:
            self._logger.error("Cannot verify ID token: JWKS not available.")
            return None

        public_keys: Dict[str, RSAPublicKey] = {}  # Explicitly type the dictionary
        try:
            for jwk in jwks_response.get("keys", []):
                if jwk.get("kty") == "RSA" and "kid" in jwk:
                    key_obj = RSAAlgorithm.from_jwk(jwk)
                    if isinstance(key_obj, RSAPublicKey):
                        public_keys[jwk["kid"]] = key_obj
                    else:
                        # Log or handle the case where a non-public key is encountered, if necessary
                        self._logger.warning(
                            f"JWK with kid '{jwk.get('kid')}' did not resolve to an RSAPublicKey. Skipping."
                        )
        except Exception as e:
            self._logger.error(f"Error processing JWK keys: {e}")
            return None

        if not public_keys:
            self._logger.error("No valid public keys found in JWKS response.")
            return None

        try:
            header = get_unverified_header(token)
            kid = header.get("kid")
            if not kid:
                self._logger.error("ID token header missing 'kid'.")
                return None

            key = public_keys.get(kid)
            if not key:
                self._logger.error(f"Public key for kid '{kid}' not found in JWKS.")
                return None

            aud = split_string(",", os.environ.get(ENV_ALLOWED_AUD, ""))
            options = {
                "verify_exp": True,
                "verify_aud": True,
                "verify_iat": True,
                "verify_nbf": True,
            }
            user = decode(
                token,
                key=key,
                algorithms=["RS256"],
                audience=aud,
                leeway=60,
                options=options,
            )

            now = datetime.now().timestamp()  # type: ignore
            expiry = user.get("exp", 0) - now
            ttl = int(expiry) if expiry > 0 else self.DEFAULT_TOKEN_TTL_SEC

            cache_key = BEARER_TOKEN_KEY_PREFIX + token
            if await self._get_resolved_async_cache_client():  # type: ignore
                await self._set_cached_value_async(cache_key, user, ttl=ttl)  # type: ignore
            else:
                self._set_cached_value(cache_key, user, ttl=ttl)  # type: ignore

            if self.ENABLE_BACKCHANNEL_LOGOUT:
                sid = user.get("sid")
                sub = user.get("sub")
                if sid:
                    await self._link_sid_to_token(sid, cache_key)  # type: ignore
                    if sub and self.ENABLE_LOGOUT_BY_SUB:
                        await self._link_sub_to_sid(sub, sid)  # type: ignore

            self._logger.info(f"ID token verified successfully for kid '{kid}'.")
            return user
        except Exception as e:
            self._logger.error(f"ID token verification failed: {e}")
            cache_key = BEARER_TOKEN_KEY_PREFIX + token
            if await self._get_resolved_async_cache_client():  # type: ignore
                await self._delete_cached_value_async(cache_key)  # type: ignore
            else:
                self._delete_cached_value(cache_key)  # type: ignore
            return None

    def fetch_userinfo(self, userinfo_url: str, token: str) -> Optional[dict]:
        """Fetches user info from the userinfo endpoint. (Synchronous Network I/O)"""
        if not userinfo_url:
            self._logger.warning("Userinfo URL not configured.")
            return None
        self._logger.info(f"Fetching userinfo from: {userinfo_url}")
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(
                userinfo_url,
                headers=headers,
                timeout=10,
                verify=self._request_verify_ssl,
            )
            response.raise_for_status()
            userinfo = response.json()
            self._logger.debug("Userinfo fetched successfully.")
            return userinfo
        except HTTPError as e:
            self._logger.error(
                f"Error fetching userinfo from {userinfo_url}: {e}", exc_info=True
            )
            return None
        except ValueError as e:  # For JSON decoding errors
            self._logger.error(
                f"ValueError decoding userinfo JSON from {userinfo_url}: {e}",
                exc_info=True,
            )
            return None
        except Exception as e:
            self._logger.error(
                f"Error fetching userinfo from {userinfo_url}: {e}", exc_info=True
            )
            return None

    async def introspect_token(self, token: str) -> Optional[dict]:
        """Introspects a token using the introspection endpoint."""
        introspection_url = os.environ.get(ENV_INTROSPECT_URL)
        if not introspection_url:
            self._logger.warning(f"{ENV_INTROSPECT_URL} environment variable not set.")
            return None

        self._logger.info(f"Introspecting token via: {introspection_url}")
        try:
            token_key_env_var = os.environ.get(ENV_INTROSPECT_TOKEN_KEY)
            token_key = (
                token_key_env_var if token_key_env_var else DEFAULT_INTROSPECT_TOKEN_KEY
            )
            data = {token_key: token}
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            }
            auth = None
            if os.environ.get(ENV_INTROSPECT_REQUIRES_AUTH, "false").lower() == "true":
                client_id = os.environ.get(ENV_CLIENT_ID)
                client_secret = os.environ.get(ENV_CLIENT_SECRET)
                if not client_id or not client_secret:
                    self._logger.error(
                        "Introspection requires auth, but client ID or secret is missing."
                    )
                    return None
                auth = (client_id, client_secret)

            response = requests.post(
                introspection_url,
                headers=headers,
                data=data,
                auth=auth,
                timeout=10,
                verify=self._request_verify_ssl,
            )
            response.raise_for_status()
            int_resp = response.json()
        except HTTPError as e:
            self._logger.error(
                f"HTTPError during token introspection: {e}", exc_info=True
            )
            return None
        except ValueError as e:  # For JSON decoding errors
            self._logger.error(
                f"ValueError decoding introspection JSON: {e}", exc_info=True
            )
            return None
        except Exception as e:
            self._logger.error(
                f"Unexpected error during token introspection: {e}", exc_info=True
            )
            return None

        cache_key = BEARER_TOKEN_KEY_PREFIX + token
        if not int_resp or not int_resp.get("active"):
            self._logger.warning("Token introspection result is inactive or invalid.")
            if await self._get_resolved_async_cache_client():  # type: ignore
                await self._delete_cached_value_async(cache_key)  # type: ignore
            else:
                self._delete_cached_value(cache_key)  # type: ignore
            return None

        if "exp" not in int_resp:  # Should this be an error or just a warning?
            self._logger.warning("Introspection response missing 'exp' field.")
            # Fallback to default TTL or handle as error? For now, cache with default.

        now = datetime.now().timestamp()
        expiry = int_resp.get("exp", 0) - now  # If 'exp' is missing, this uses 0
        ttl = int(expiry) if expiry > 0 else self.DEFAULT_TOKEN_TTL_SEC

        if await self._get_resolved_async_cache_client():  # type: ignore
            await self._set_cached_value_async(cache_key, int_resp, ttl=ttl)  # type: ignore
        else:
            self._set_cached_value(cache_key, int_resp, ttl=ttl)  # type: ignore
        self._logger.info("Token introspection successful and cached.")

        if os.environ.get(ENV_ENABLE_FETCH_USERINFO, "false").lower() == "true":
            userinfo_url = os.environ.get(ENV_USERINFO_URL)
            if userinfo_url:
                userinfo = await asyncio.to_thread(
                    self.fetch_userinfo, userinfo_url, token
                )
                if userinfo:
                    merged_info = userinfo | int_resp
                    if await self._get_resolved_async_cache_client():  # type: ignore
                        await self._set_cached_value_async(cache_key, merged_info, ttl=ttl)  # type: ignore
                    else:
                        self._set_cached_value(cache_key, merged_info, ttl=ttl)  # type: ignore
                    self._logger.debug(
                        "Userinfo fetched and merged into cached token data."
                    )
                    return merged_info
            else:
                self._logger.warning(
                    f"{ENV_USERINFO_URL} not set, skipping userinfo fetch."
                )
        return int_resp
