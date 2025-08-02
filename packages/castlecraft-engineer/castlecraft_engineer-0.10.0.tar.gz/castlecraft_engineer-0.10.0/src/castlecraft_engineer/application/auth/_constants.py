from castlecraft_engineer.common.env import DEFAULT_AUTH_TOKEN_TTL_SEC

BEARER_TOKEN_KEY_PREFIX = "bearer_token|"
JWKS_RESPONSE_KEY = "jwks_response"

BACKCHANNEL_LOGOUT_SID_MAP_PREFIX = "bcl_sid_map|"
BACKCHANNEL_LOGOUT_SUB_MAP_PREFIX = "bcl_sub_map|"
BACKCHANNEL_LOGOUT_EVENT_CLAIM = "http://schemas.openid.net/event/backchannel-logout"

# Default TTLs for backchannel logout, derived from common env defaults
# sid will be kept for time twice the default token TTL
DEFAULT_BACKCHANNEL_SID_MAP_TTL_SEC = int(DEFAULT_AUTH_TOKEN_TTL_SEC) * 2
# sub will be kept for time longer than sid map ttl
DEFAULT_BACKCHANNEL_SUB_MAP_TTL_SEC = int(DEFAULT_AUTH_TOKEN_TTL_SEC) * 3
