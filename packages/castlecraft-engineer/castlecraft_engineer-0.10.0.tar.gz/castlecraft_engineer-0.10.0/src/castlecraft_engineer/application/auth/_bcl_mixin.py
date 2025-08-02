from typing import Dict, Optional  # Add import

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey  # Add import
from jwt import decode, get_unverified_header
from jwt.algorithms import RSAAlgorithm

from ._base import AuthenticationServiceBase
from ._constants import (  # Import constants
    BACKCHANNEL_LOGOUT_EVENT_CLAIM,
    BACKCHANNEL_LOGOUT_SID_MAP_PREFIX,
    BACKCHANNEL_LOGOUT_SUB_MAP_PREFIX,
)


class BackchannelLogoutMixin(AuthenticationServiceBase):
    async def _link_sub_to_sid(self, sub: str, sid: str):
        """Helper to create/update the SUB-to-SID mapping in async cache."""
        if not self.ENABLE_LOGOUT_BY_SUB:
            return
        async_cache_client = await self._get_resolved_async_cache_client()  # type: ignore
        if not async_cache_client or not sub or not sid:
            self._logger.debug("Async cache, SUB, or SID not available for linking.")
            return
        sub_map_key = BACKCHANNEL_LOGOUT_SUB_MAP_PREFIX + sub
        try:
            await async_cache_client.sadd(sub_map_key, sid)
            await async_cache_client.expire(
                sub_map_key, self.BACKCHANNEL_SUB_MAP_TTL_SEC
            )
            self._logger.debug(f"Linked SID {sid} to SUB {sub} in map {sub_map_key}.")
        except Exception as e:
            self._logger.error(f"Error linking SUB {sub} to SID {sid} in cache: {e}")

    async def _unlink_sub_from_sid(self, sub: str, sid: str):
        """Helper to remove an SID from a SUB mapping in async cache."""
        if not self.ENABLE_LOGOUT_BY_SUB:
            return
        async_cache_client = await self._get_resolved_async_cache_client()  # type: ignore
        if not async_cache_client or not sub or not sid:
            self._logger.debug("Async cache, SUB, or SID not available for unlinking.")
            return
        sub_map_key = BACKCHANNEL_LOGOUT_SUB_MAP_PREFIX + sub
        try:
            await async_cache_client.srem(sub_map_key, sid)
            self._logger.debug(
                f"Unlinked SID {sid} from SUB {sub} in map {sub_map_key}."
            )
        except Exception as e:
            self._logger.error(
                f"Error unlinking SUB {sub} from SID {sid} in cache: {e}"
            )

    async def _link_sid_to_token(self, sid: str, token_cache_key: str):
        """Helper to create/update the SID-to-token mapping in async cache."""
        if not self.ENABLE_BACKCHANNEL_LOGOUT:
            return
        async_cache_client = await self._get_resolved_async_cache_client()  # type: ignore
        if not async_cache_client or not sid or not token_cache_key:
            self._logger.debug(
                "Async cache, SID, or token_cache_key not available for linking."
            )
            return
        sid_map_key = BACKCHANNEL_LOGOUT_SID_MAP_PREFIX + sid
        try:
            await async_cache_client.sadd(sid_map_key, token_cache_key)
            await async_cache_client.expire(
                sid_map_key, self.BACKCHANNEL_SID_MAP_TTL_SEC
            )
            self._logger.debug(
                f"Linked token {token_cache_key} to SID {sid} in map {sid_map_key}."
            )
        except Exception as e:
            self._logger.error(
                f"Error linking SID {sid} to token {token_cache_key} in cache: {e}"
            )

    async def _unlink_sid_from_token(self, sid: str, token_cache_key: str):
        """Helper to remove a token from an SID mapping in async cache."""
        if not self.ENABLE_BACKCHANNEL_LOGOUT:
            return
        async_cache_client = await self._get_resolved_async_cache_client()  # type: ignore
        if not async_cache_client or not sid or not token_cache_key:
            self._logger.debug(
                "Async cache, SID, or token_cache_key not available for unlinking."
            )
            return
        sid_map_key = BACKCHANNEL_LOGOUT_SID_MAP_PREFIX + sid
        try:
            await async_cache_client.srem(sid_map_key, token_cache_key)
            self._logger.debug(
                f"Unlinked token {token_cache_key} from SID {sid} in map {sid_map_key}."
            )
        except Exception as e:
            self._logger.error(
                f"Error unlinking SID {sid} from token {token_cache_key} in cache: {e}"
            )

    async def validate_backchannel_logout_token(
        self, logout_token_jwt: str
    ) -> Optional[dict]:
        """Validates a backchannel logout token."""
        if not self.ENABLE_BACKCHANNEL_LOGOUT:
            self._logger.info(
                "Backchannel logout support disabled, validation skipped."
            )
            return None
        if (
            not self.BACKCHANNEL_LOGOUT_TOKEN_ISS
            or not self.BACKCHANNEL_LOGOUT_TOKEN_AUD
        ):
            self._logger.error(
                "Backchannel logout token validation requires configured issuer and audience."
            )
            return None

        jwks_response = await self.get_active_jwks_response()  # type: ignore
        if not jwks_response:
            self._logger.error("Cannot validate logout token: JWKS not available.")
            return None

        public_keys: Dict[str, RSAPublicKey] = {}  # Explicitly type the dictionary
        try:
            for jwk in jwks_response.get("keys", []):
                if jwk.get("kty") == "RSA" and "kid" in jwk:
                    key_obj = RSAAlgorithm.from_jwk(jwk)
                    if isinstance(key_obj, RSAPublicKey):
                        public_keys[jwk["kid"]] = key_obj
                    else:
                        self._logger.warning(
                            f"JWK with kid '{jwk.get('kid')}' in BCL did not resolve to an RSAPublicKey. Skipping."
                        )
        except Exception as e:
            self._logger.error(f"Error processing JWK keys for logout token: {e}")
            return None
        if not public_keys:
            self._logger.error("No valid public keys in JWKS for logout token.")
            return None

        try:
            header = get_unverified_header(logout_token_jwt)
            kid = header.get("kid")
            if not kid:
                self._logger.error("Logout token header missing 'kid'.")
                return None
            key = public_keys.get(kid)
            if not key:
                self._logger.error(
                    f"Public key for kid '{kid}' not found for logout token."
                )
                return None

            options = {
                "verify_exp": True,
                "require": ["iss", "aud", "iat", "exp", "jti", "events"],
                "verify_aud": True,
                "verify_iat": True,
                "verify_nbf": True,
            }
            claims = decode(
                logout_token_jwt,
                key=key,
                algorithms=["RS256"],  # type: ignore
                audience=self.BACKCHANNEL_LOGOUT_TOKEN_AUD,
                issuer=self.BACKCHANNEL_LOGOUT_TOKEN_ISS,
                leeway=60,
                options=options,
            )

            if not claims.get("sid") and not claims.get("sub"):
                self._logger.error("Logout token MUST contain 'sid' or 'sub' claim.")
                return None
            events = claims.get("events")
            if (
                not isinstance(events, dict)
                or BACKCHANNEL_LOGOUT_EVENT_CLAIM not in events
            ):
                self._logger.error(
                    f"Logout token missing/invalid 'events' for '{BACKCHANNEL_LOGOUT_EVENT_CLAIM}'."
                )
                return None
            if (
                not isinstance(events[BACKCHANNEL_LOGOUT_EVENT_CLAIM], dict)
                or events[BACKCHANNEL_LOGOUT_EVENT_CLAIM]
            ):
                self._logger.error(
                    f"Logout token 'events' for '{BACKCHANNEL_LOGOUT_EVENT_CLAIM}' not empty JSON object."
                )
                return None
            if "nonce" in claims:
                self._logger.error("Logout token must not contain a 'nonce' claim.")
                return None

            self._logger.info(
                f"Backchannel logout token validated successfully for kid '{kid}'."
            )
            return claims
        except Exception as e:
            self._logger.error(
                f"Backchannel logout token validation failed: {e}", exc_info=True
            )
            return None

    async def invalidate_sessions_by_sid(
        self, sid: str, sub: Optional[str] = None
    ) -> bool:
        """Invalidates all cached tokens associated with a given SID."""
        if not self.ENABLE_BACKCHANNEL_LOGOUT:
            self._logger.info("BCL disabled. invalidate_sessions_by_sid ignored.")
            return False
        if not sid:
            self._logger.warning("invalidate_sessions_by_sid called with empty SID.")
            return False
        async_cache_client = await self._get_resolved_async_cache_client()  # type: ignore
        if not async_cache_client:
            self._logger.error(
                "Async cache not available for invalidate_sessions_by_sid."
            )
            return False

        sid_map_key = BACKCHANNEL_LOGOUT_SID_MAP_PREFIX + sid
        try:
            self._logger.info(f"Attempting to invalidate sessions for SID: {sid}")
            token_cache_keys_bytes = await async_cache_client.smembers(sid_map_key)
            if token_cache_keys_bytes:
                for token_key_bytes in token_cache_keys_bytes:
                    token_key = token_key_bytes.decode("utf-8")
                    self._logger.info(f"Invalidating token (SID: {sid}): {token_key}")
                    if self.ENABLE_LOGOUT_BY_SUB and sub is None:
                        payload = await self._get_cached_value_async(token_key)  # type: ignore
                        if isinstance(payload, dict) and payload.get("sub"):
                            sub = payload.get("sub")
                    await self._delete_cached_value_async(token_key)  # type: ignore
            await async_cache_client.delete(sid_map_key)
            self._logger.info(f"Token sessions for SID {sid} invalidated.")
            if self.ENABLE_LOGOUT_BY_SUB and sub:
                await self._unlink_sub_from_sid(sub, sid)
            return True
        except Exception as e:
            self._logger.error(
                f"Error invalidating sessions for SID {sid}: {e}", exc_info=True
            )
            return False

    async def invalidate_sessions_by_sub(self, sub: str) -> bool:
        """Invalidates all cached SIDs (and their tokens) for a given SUB."""
        if not self.ENABLE_LOGOUT_BY_SUB:
            self._logger.info(
                "Logout by SUB disabled. invalidate_sessions_by_sub ignored."
            )
            return False
        if not sub:
            self._logger.warning("invalidate_sessions_by_sub called with empty SUB.")
            return False
        async_cache_client = await self._get_resolved_async_cache_client()  # type: ignore
        if not async_cache_client:
            self._logger.error(
                "Async cache not available for invalidate_sessions_by_sub."
            )
            return False

        sub_map_key = BACKCHANNEL_LOGOUT_SUB_MAP_PREFIX + sub
        sids_invalidated_count = 0
        try:
            self._logger.info(f"Attempting to invalidate SIDs for SUB: {sub}")
            sids_bytes = await async_cache_client.smembers(sub_map_key)
            if not sids_bytes:
                self._logger.info(f"No active SIDs found for SUB: {sub}")
                await async_cache_client.delete(sub_map_key)
                return True

            sids_to_invalidate = [s.decode("utf-8") for s in sids_bytes]
            for sid_to_invalidate in sids_to_invalidate:
                await self.invalidate_sessions_by_sid(sid_to_invalidate, sub=sub)
                sids_invalidated_count += 1
            await async_cache_client.delete(sub_map_key)
            self._logger.info(
                f"Processed {sids_invalidated_count} SID(s) for SUB: {sub}"
            )
            return True
        except Exception as e:
            self._logger.error(
                f"Error invalidating sessions for SUB {sub}: {e}", exc_info=True
            )
            return False
