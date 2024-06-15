from datetime import datetime, timedelta

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, OAuth2PasswordBearer

from api.db.cache import redis as cache
from api.db.implements.mongo import get_user_by_email
from api.db.implements.redis import AuthManager
from api.settings import env
from enums.auth import GrantType, OAuthProvider
from schemas.auth import TokenPayload
from schemas.users import UserInfo

# Token url
# 나중에 필요하다면 자체 토큰 인증을 위한 url을 만들 수 있지만
# 현재는 OAuth2 Service provider를 이용하기 때문에 tokenUrl은 임의의 값을 넣어도 상관없다.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# 현재는 대부분의 엔드포인트가 bearer token을 필요로 하기 때문에
# oauth2_scheme를 wrapper로 감싸서 사용하는 bearer_scheme를 만들었다.
bearer_scheme = HTTPBearer()

# Error
CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


# Create token internal function
def _create_access_token(*, data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire, "type": GrantType.ACCESS_TOKEN})
    encoded_jwt = jwt.encode(
        to_encode,
        env.app_secret,
        algorithm=env.app_secret_algo,
    )
    return encoded_jwt


def _create_refresh_token(*, data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=30)
    to_encode.update({"exp": expire, "type": GrantType.REFRESH_TOKEN})
    encoded_jwt = jwt.encode(
        to_encode,
        env.app_secret,
        algorithm=env.app_secret_algo,
    )
    return encoded_jwt


def create_access_token(email: str, auth_provider: OAuthProvider) -> str:
    """
    Create access token for an email
    """
    access_token_expires = timedelta(minutes=env.app_access_token_expire_minutes)
    access_token = _create_access_token(
        data={"email": email, "auth_provider": auth_provider},
        expires_delta=access_token_expires,
    )
    return access_token


def create_refresh_token(email: str, auth_provider: OAuthProvider) -> str:
    """
    Create refresh token for an email
    """
    refresh_token_expires = timedelta(minutes=env.app_refresh_token_expire_minutes)
    refresh_token = _create_refresh_token(
        data={"email": email, "auth_provider": auth_provider},
        expires_delta=refresh_token_expires,
    )
    return refresh_token


async def valid_email_from_db(
    email: str,
    auth_provider: OAuthProvider,
) -> UserInfo | None:
    user_model = await get_user_by_email(
        email=email,
        auth_provider=auth_provider,
    )
    if not user_model:
        return None
    return UserInfo(**user_model.model_dump())


async def get_current_user_email(token: str = Depends(oauth2_scheme)) -> TokenPayload:
    auth_manager = AuthManager(cache)
    if await auth_manager.is_token_in_blacklist(token):
        raise CREDENTIALS_EXCEPTION
    try:
        payload = decode_token(token)
        email: str = payload.get("email")
        if email is None:
            raise CREDENTIALS_EXCEPTION
        auth_provider: OAuthProvider = payload.get("auth_provider")
        if auth_provider is None:
            raise CREDENTIALS_EXCEPTION
    except jwt.PyJWTError as jwt_error:
        raise CREDENTIALS_EXCEPTION from jwt_error
    if await valid_email_from_db(email, auth_provider):
        return TokenPayload(email=email, auth_provider=auth_provider)
    raise CREDENTIALS_EXCEPTION


async def get_current_user_email_bearer(
    token=Depends(bearer_scheme),
) -> TokenPayload:
    token_payload: TokenPayload = await get_current_user_email(token.credentials)
    if token_payload is None:
        raise CREDENTIALS_EXCEPTION
    return token_payload


async def get_current_user_bearer(token=Depends(bearer_scheme)) -> UserInfo:
    token_payload: TokenPayload = await get_current_user_email(token.credentials)
    if token_payload.email is None:
        raise CREDENTIALS_EXCEPTION
    if token_payload.auth_provider is None:
        raise CREDENTIALS_EXCEPTION
    user_info = await get_user_by_email(
        token_payload.email, token_payload.auth_provider
    )
    if user_info is None:
        raise CREDENTIALS_EXCEPTION
    return UserInfo(**user_info.model_dump())


async def get_current_user_id_bearer(token: str = Depends(bearer_scheme)) -> str:
    user_info = await get_current_user_bearer(token)
    user_id = user_info.id
    return user_id


def decode_token(token):
    return jwt.decode(token, env.app_secret, algorithms=[env.app_secret_algo])
