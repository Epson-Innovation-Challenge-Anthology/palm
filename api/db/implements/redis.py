import logging
from datetime import timedelta

from api.db.cache import Redis
from api.errors import BlacklistTokenError
from api.settings import env
from schemas.auth import GrantType


class AuthManager:
    def __init__(self, redis: Redis):
        self.core = redis

    async def add_token_to_blacklist(self, token, grant_type: GrantType) -> bool:
        key = self.core.mangle_key("blacklist", token)
        if grant_type == GrantType.ACCESS_TOKEN:
            try:
                redis = self.core.get_redis()
                await redis.set(
                    name=key,
                    value="access_token",
                    ex=timedelta(minutes=env.app_access_token_expire_minutes),
                )
            except BlacklistTokenError as e:
                logging.exception(e)
                return False
        else:
            try:
                redis = self.core.get_redis()
                await redis.set(
                    name=key,
                    value="refresh_token",
                    ex=timedelta(minutes=env.app_refresh_token_expire_minutes),
                )
            except BlacklistTokenError as e:
                logging.exception(e)
                return False
        return True

    async def is_token_in_blacklist(self, token) -> bool:
        key = self.core.mangle_key("blacklist", token)
        redis = self.core.get_redis()
        return await redis.exists(key)
