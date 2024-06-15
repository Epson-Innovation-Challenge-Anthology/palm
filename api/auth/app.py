import logging
from datetime import datetime, timedelta
from pathlib import Path

import aiohttp
from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import Depends, FastAPI, Request, status
from fastapi.openapi.utils import get_openapi
from google.auth.transport import requests
from google.oauth2 import id_token
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware

from api.db.cache import redis as cache
from api.db.implements.mongo import add_token_log, add_user
from api.db.implements.redis import AuthManager
from api.errors import GoogleModuleError, KakaoModuleError
from api.jwt import (
    CREDENTIALS_EXCEPTION,
    bearer_scheme,
    create_access_token,
    create_refresh_token,
    decode_token,
    valid_email_from_db,
)
from api.settings import env, get_description
from enums.auth import AuthMessage, EventType, GrantType, OAuthProvider
from responses import auth as auth_response
from responses.common import custom_response
from schemas import ResponseModel
from schemas.auth import (
    AccessTokenResponse,
    IDTokenBody,
    RefreshBody,
    TokenLog,
    TokenResponse,
)
from schemas.users import UserInfo, UserModel

BASE_PATH = Path(__file__)

# Create the auth app
auth_app = FastAPI(
    title=f"{env.service_name} Auth",
    description=get_description(base_path=BASE_PATH),
    version=env.app_version,
    openapi_tags=[
        {
            "name": "auth",
            "description": "인증 관련 기능",
        },
    ],
)


@auth_app.middleware("http")
async def add_process_time_header(request, call_next):
    response = await call_next(request)
    return response


def custom_openapi():
    if not auth_app.openapi_schema:
        auth_app.openapi_schema = get_openapi(
            title=auth_app.title,
            version=auth_app.version,
            openapi_version=auth_app.openapi_version,
            description=auth_app.description,
            terms_of_service=auth_app.terms_of_service,
            contact=auth_app.contact,
            license_info=auth_app.license_info,
            routes=auth_app.routes,
            tags=auth_app.openapi_tags,
            servers=auth_app.servers,
        )

        for _end_point, method_item in auth_app.openapi_schema.get("paths", {}).items():
            for _method, param in method_item.items():
                responses = param.get("responses")
                if "204" in responses:
                    pass
                if "302" in responses:
                    del responses["302"]
                if "422" in responses:
                    del responses["422"]
    return auth_app.openapi_schema


# OAuth settings
GOOGLE_CLIENT_ID = env.google_client_id
GOOGLE_CLIENT_SECRET = env.google_client_secret
KAKAO_CLIENT_ID = env.kakao_client_id
KAKAO_CLIENT_SECRET = env.kakao_client_secret

# Set up OAuth
config_data = {
    "GOOGLE_CLIENT_ID": GOOGLE_CLIENT_ID,
    "GOOGLE_CLIENT_SECRET": GOOGLE_CLIENT_SECRET,
    "KAKAO_CLIENT_ID": KAKAO_CLIENT_ID,
}
starlette_config = Config(environ=config_data)
oauth = OAuth(starlette_config)
oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email"},
)
oauth.register(
    name="kakao",
    authorize_url="https://kauth.kakao.com/oauth/authorize",
    # access_token_url="https://kauth.kakao.com/oauth/token",
    client_kwargs={"scope": "openid,profile_nickname,account_email"},
)

# Set up the middleware to read the request session
SECRET_KEY = env.app_secret
auth_app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# --- kakao ---


@auth_app.post(
    "/kakao/token/signin",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": AuthMessage.TOKEN_OKAY,
            "model": ResponseModel[TokenResponse],
        },
    },
    tags=["kakao"],
    include_in_schema=False,
)
async def kakao_signin(body: IDTokenBody):
    """
    ID Token의 무결성을 확인하고 access_token을 발급합니다.
    이 과정에서 사용자가 회원가입되어있지 않으면 DB에 회원정보를 추가합니다.
    """
    users_id_token = body.id_token
    signup_complete = True

    async with aiohttp.ClientSession(
        headers={
            "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
        }
    ) as session:
        async with session.post(
            "https://kauth.kakao.com/oauth/tokeninfo",
            data={
                "id_token": users_id_token,
            },
        ) as response:
            user_data = await response.json()
            logging.debug("user_data: %s", user_data)
            if user_data.get("error"):
                raise CREDENTIALS_EXCEPTION
            if user_data.get("iss") not in ["https://kauth.kakao.com"]:
                raise CREDENTIALS_EXCEPTION
    try:
        user_: UserModel = UserModel(
            auth_provider=OAuthProvider.KAKAO,
            email=user_data.get("email"),
            name=user_data.get("nickname"),
        )
        user_info = await valid_email_from_db(
            email=user_.email,
            auth_provider=OAuthProvider.KAKAO,
        )

        if not user_info:
            signup_complete = False
            user_created, user_ = await add_user(user=user_)
            if not user_created:
                raise CREDENTIALS_EXCEPTION  # user not created
            user_info = UserInfo(**user_.model_dump())
    except Exception as user_error:
        logging.exception("user error: %s", user_error)
        raise CREDENTIALS_EXCEPTION from user_error

    access_token_ = create_access_token(
        email=user_info.email, auth_provider=OAuthProvider.KAKAO
    )
    refresh_token_ = create_refresh_token(
        email=user_info.email, auth_provider=OAuthProvider.KAKAO
    )
    response_model = TokenResponse(
        access_token=access_token_,
        refresh_token=refresh_token_,
        signup_complete=signup_complete,
    )
    created_at_ = datetime.now()

    await add_token_log(
        payload=TokenLog(
            user_id=user_info.id,
            event_type=EventType.SIGNIN,
            access_token=access_token_,
            refresh_token=refresh_token_,
            grant_type=GrantType.REFRESH_TOKEN,
            created_at=created_at_.strftime("%Y-%m-%d %H:%M:%S"),
            expired_at=(
                created_at_
                + timedelta(
                    minutes=env.app_refresh_token_expire_minutes,
                )
            ).strftime("%Y-%m-%d %H:%M:%S"),
        )
    )
    return custom_response(
        status_code=status.HTTP_200_OK,
        content=ResponseModel[TokenResponse](
            message=AuthMessage.TOKEN_OKAY,
            data=response_model,
        ),
    )


@auth_app.get(
    "/kakao/login",
    status_code=302,
    responses={
        302: {
            "description": "Redirect to Kakao OAuth",
            "content": {
                "application/text": {"example": "Redirecting..."},
            },
        }
    },
    tags=["kakao"],
    include_in_schema=False,
)
async def kakao_web_login(request: Request):
    """
    웹로그인 기능, [로컬, 개발] 환경에서만 사용될 예정

    Login에 성공하면 /auth/token으로 redirect 됩니다.
    """
    redirect_uri = f"{env.frontend_url}/auth/kakao/token"
    if not oauth.kakao:
        raise KakaoModuleError
    logging.debug(oauth.kakao)
    return await oauth.kakao.authorize_redirect(request, redirect_uri)


@auth_app.get(
    "/kakao/token",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": AuthMessage.TOKEN_OKAY,
            "model": ResponseModel[TokenResponse],
        },
    },
    tags=["kakao"],
    include_in_schema=False,
)
async def kakao_auth(request: Request):
    """
    직접 호출할 일은 없지만 로그인에 성공하면 이곳으로 redirect 됩니다.
    """
    signup_complete = True
    async with aiohttp.ClientSession(
        headers={
            "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
        }
    ) as session:
        async with session.post(
            "https://kauth.kakao.com/oauth/token",
            data={
                "grant_type": "authorization_code",
                "client_id": KAKAO_CLIENT_ID,
                "redirect_uri": f"{env.frontend_url}/auth/kakao/token",
                "code": request.query_params.get("code"),
                "client_secret": KAKAO_CLIENT_SECRET,
            },
        ) as response:
            access_token = await response.json()
            logging.debug("access_token: %s", access_token)
            if access_token.get("error"):
                raise CREDENTIALS_EXCEPTION
        async with session.post(
            "https://kauth.kakao.com/oauth/tokeninfo",
            data={
                "id_token": access_token.get("id_token", ""),
            },
        ) as response:
            user_data = await response.json()
            logging.info("user_data: %s", user_data)
            if user_data.get("error"):
                raise CREDENTIALS_EXCEPTION
    try:
        user_: UserModel = UserModel(
            auth_provider=OAuthProvider.KAKAO,
            email=user_data.get("email"),
            name=user_data.get("nickname"),
        )
        user_info = await valid_email_from_db(
            email=user_.email,
            auth_provider=OAuthProvider.KAKAO,
        )
        if not user_info:
            signup_complete = False
            _okay, user_ = await add_user(user=user_)
            user_info = UserInfo(**user_.model_dump())
    except Exception as user_error:
        logging.exception("user error: %s", user_error)
        raise CREDENTIALS_EXCEPTION from user_error

    access_token_ = create_access_token(
        email=user_info.email, auth_provider=OAuthProvider.KAKAO
    )
    refresh_token_ = create_refresh_token(
        email=user_info.email, auth_provider=OAuthProvider.KAKAO
    )
    response_model = TokenResponse(
        access_token=access_token_,
        refresh_token=refresh_token_,
        signup_complete=signup_complete,
    )
    created_at_ = datetime.utcnow()

    await add_token_log(
        payload=TokenLog(
            user_id=user_info.id,
            event_type=EventType.SIGNIN,
            access_token=access_token_,
            refresh_token=refresh_token_,
            grant_type=GrantType.REFRESH_TOKEN,
            created_at=created_at_.strftime("%Y-%m-%d %H:%M:%S"),
            expired_at=(
                created_at_
                + timedelta(
                    minutes=env.app_refresh_token_expire_minutes,
                )
            ).strftime("%Y-%m-%d %H:%M:%S"),
        )
    )
    return custom_response(
        status_code=status.HTTP_200_OK,
        content=ResponseModel[TokenResponse](
            message=AuthMessage.TOKEN_OKAY,
            data=response_model,
        ),
    )


# --- google ---


@auth_app.get(
    "/google/token",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": AuthMessage.TOKEN_OKAY,
            "model": ResponseModel[TokenResponse],
        },
    },
    tags=["google"],
    include_in_schema=False,
)
async def google_auth(request: Request):
    """
    직접 호출할 일은 없지만 로그인에 성공하면 이곳으로 redirect 됩니다.
    """
    signup_complete = True
    try:
        if not oauth.google:
            raise GoogleModuleError
        logging.info("request: %s", request)
        access_token = await oauth.google.authorize_access_token(request)
        logging.info("access_token: %s", access_token)
    except OAuthError as oauth_error:
        # csrf issue or denied by user
        logging.info("oauth_error: %s", oauth_error)
        raise CREDENTIALS_EXCEPTION from oauth_error
    logging.debug("access_token: %s", access_token)
    user_data = access_token.get("userinfo")
    if not user_data:
        logging.warning("not user data")
        raise CREDENTIALS_EXCEPTION

    try:
        user_ = UserInfo(auth_provider=OAuthProvider.GOOGLE, **user_data)
        user_info = await valid_email_from_db(
            email=user_.email,
            auth_provider=OAuthProvider.GOOGLE,
        )
        if not user_info:
            signup_complete = False
            _okay, user_ = await add_user(user=user_)  # type: ignore
            user_info = UserInfo(**user_.model_dump())
    except Exception as user_error:
        logging.exception("user error: %s", user_error)
        raise CREDENTIALS_EXCEPTION from user_error

    access_token_ = create_access_token(
        email=user_info.email, auth_provider=OAuthProvider.GOOGLE
    )
    refresh_token_ = create_refresh_token(
        email=user_info.email, auth_provider=OAuthProvider.GOOGLE
    )
    response_model = TokenResponse(
        access_token=access_token_,
        refresh_token=refresh_token_,
        signup_complete=signup_complete,
    )
    created_at_ = datetime.now()

    await add_token_log(
        payload=TokenLog(
            user_id=user_info.id,
            event_type=EventType.SIGNIN,
            access_token=access_token_,
            refresh_token=refresh_token_,
            grant_type=GrantType.REFRESH_TOKEN,
            created_at=created_at_.strftime("%Y-%m-%d %H:%M:%S"),
            expired_at=(
                created_at_
                + timedelta(
                    minutes=env.app_refresh_token_expire_minutes,
                )
            ).strftime("%Y-%m-%d %H:%M:%S"),
        )
    )
    return custom_response(
        status_code=status.HTTP_200_OK,
        content=ResponseModel[TokenResponse](
            message=AuthMessage.TOKEN_OKAY,
            data=response_model,
        ),
    )


@auth_app.post(
    "/token/signin",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": AuthMessage.TOKEN_OKAY,
            "model": ResponseModel[TokenResponse],
        },
    },
    tags=["auth"],
    deprecated=False,
    include_in_schema=False,
)
@auth_app.post(
    "/google/token/signin",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": AuthMessage.TOKEN_OKAY,
            "model": ResponseModel[TokenResponse],
        },
    },
    tags=["google"],
)
async def google_signin(body: IDTokenBody):
    """
    클라이언트 사이드에서 구글 로그인을 진행하고 ID Token을 받아서 서버로 전송할 목적으로 사용합니다.

    ID Token의 무결성을 확인하고 access_token을 발급합니다.
    이 과정에서 사용자가 회원가입되어있지 않으면 DB에 회원정보를 추가합니다.
    """
    users_id_token = body.id_token
    signup_complete = True

    try:
        idinfo = id_token.verify_oauth2_token(
            id_token=users_id_token,
            request=requests.Request(),
            audience=GOOGLE_CLIENT_ID,
        )
        if idinfo["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
            raise ValueError("Wrong issuer.")
        email = idinfo["email"]

        user_info = await valid_email_from_db(
            email=email, auth_provider=OAuthProvider.GOOGLE
        )
        user_ = None  # type: ignore
        if not user_info:
            signup_complete = False
            _okay, user_ = await add_user(
                UserModel(
                    **idinfo,
                    auth_provider=OAuthProvider.GOOGLE,
                ),
            )
            user_info = UserInfo(**user_.model_dump())

        access_token_ = create_access_token(
            email=user_info.email, auth_provider=OAuthProvider.GOOGLE
        )
        refresh_token_ = create_refresh_token(
            email=user_info.email, auth_provider=OAuthProvider.GOOGLE
        )
        response_model = TokenResponse(
            access_token=access_token_,
            refresh_token=refresh_token_,
            signup_complete=signup_complete,
        )
        created_at_ = datetime.now()

        await add_token_log(
            payload=TokenLog(
                user_id=user_info.id,
                event_type=EventType.SIGNIN,
                access_token=access_token_,
                refresh_token=refresh_token_,
                grant_type=GrantType.REFRESH_TOKEN,
                created_at=created_at_.strftime("%Y-%m-%d %H:%M:%S"),
                expired_at=(
                    created_at_
                    + timedelta(
                        minutes=env.app_refresh_token_expire_minutes,
                    )
                ).strftime("%Y-%m-%d %H:%M:%S"),
            )
        )
        return custom_response(
            status_code=status.HTTP_200_OK,
            content=ResponseModel[TokenResponse](
                message=AuthMessage.TOKEN_OKAY,
                data=response_model,
            ),
        )
    except ValueError as value_error:
        logging.exception("ValueError: %s", value_error)
        raise CREDENTIALS_EXCEPTION from value_error
    except Exception as credentials_error:
        logging.exception("credentials error: %s", credentials_error)
        raise CREDENTIALS_EXCEPTION from credentials_error


@auth_app.get(
    "/login",
    status_code=302,
    responses={
        302: {
            "description": "Redirect to Google OAuth",
            "content": {
                "application/text": {"example": "Redirecting..."},
            },
        }
    },
    tags=["auth"],
    deprecated=False,
    include_in_schema=False,
)
@auth_app.get(
    "/google/login",
    status_code=302,
    responses={
        302: {
            "description": "Redirect to Google OAuth",
            "content": {
                "application/text": {"example": "Redirecting..."},
            },
        }
    },
    tags=["google"],
)
async def google_web_login(request: Request):
    """
    웹로그인 기능, 서버사이드에서 모두 처리\n
    Login에 성공하면 /auth/token으로 redirect 이후 토큰정보를 반환합니다.
    """
    redirect_uri = f"{env.frontend_url}/auth/google/token"
    if not oauth.google:
        raise GoogleModuleError
    return await oauth.google.authorize_redirect(request, redirect_uri)


# --- common ---


@auth_app.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": AuthMessage.TOKEN_REFRESH_OKAY,
            "model": ResponseModel[AccessTokenResponse],
        },
    },
    tags=["auth"],
)
async def refresh(body: RefreshBody):
    """
    refresh_token을 사용하여 access_token을 재발급합니다.
    """
    try:
        token = body.refresh_token
        payload = decode_token(token)
        logging.debug("payload: %s", payload)
        logging.debug("body.grant_type: %s", body.grant_type)
        logging.debug("GrantType.REFRESH_TOKEN: %s", GrantType.REFRESH_TOKEN)
        if (
            body.grant_type != GrantType.REFRESH_TOKEN
            or payload.get("type") != GrantType.REFRESH_TOKEN.value
        ):
            raise CREDENTIALS_EXCEPTION
        # check if token is not expired
        if datetime.utcfromtimestamp(payload.get("exp")) > datetime.utcnow():
            email = payload.get("email")
            auth_provider = payload.get("auth_provider")
            # validate email
            user_info = await valid_email_from_db(
                email=email, auth_provider=auth_provider
            )
            if user_info:
                # create and return token
                created_at_ = datetime.utcnow()
                access_token_ = create_access_token(
                    email=email, auth_provider=auth_provider
                )

                await add_token_log(
                    payload=TokenLog(
                        user_id=user_info.id,
                        event_type=EventType.REFRESH_ACCESS_TOKEN,
                        access_token=access_token_,
                        refresh_token=body.refresh_token,
                        grant_type=GrantType.ACCESS_TOKEN,
                        created_at=created_at_.strftime("%Y-%m-%d %H:%M:%S"),
                        expired_at=(
                            created_at_
                            + timedelta(
                                minutes=env.app_access_token_expire_minutes,
                            )
                        ).strftime("%Y-%m-%d %H:%M:%S"),
                    )
                )

                return custom_response(
                    status_code=status.HTTP_200_OK,
                    content=ResponseModel[AccessTokenResponse](
                        message=AuthMessage.TOKEN_REFRESH_OKAY,
                        data=AccessTokenResponse(
                            access_token=access_token_,
                        ),
                    ),
                )
    except Exception as credentials_error:
        logging.exception("refresh token error: %s", credentials_error)
        raise CREDENTIALS_EXCEPTION from credentials_error
    raise CREDENTIALS_EXCEPTION


@auth_app.get(
    "/logout",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": AuthMessage.LOGOUT_SUCCESS,
            "model": ResponseModel[None],
        },
    },
    tags=["auth"],
)
async def logout(used_token=Depends(bearer_scheme)):
    """
    로그아웃시 사용하던 토큰은 블랙리스트에 추가되어 더이상 사용할 수 없어요.
    """
    used_token_ = used_token.credentials
    auth_manager = AuthManager(cache)
    okay = await auth_manager.add_token_to_blacklist(
        token=used_token_,
        grant_type=GrantType.ACCESS_TOKEN,
    )
    if okay:
        await add_token_log(
            payload=TokenLog(
                user_id=None,
                event_type=EventType.SIGNOUT,
                access_token=used_token_,
                refresh_token=None,
                grant_type=GrantType.ACCESS_TOKEN,
                created_at=None,
                expired_at=None,
                blacklisted_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            )
        )

        return custom_response(
            status_code=status.HTTP_200_OK,
            content=ResponseModel[None](
                message=AuthMessage.LOGOUT_SUCCESS,
                data=None,
            ),
        )
    raise CREDENTIALS_EXCEPTION


auth_app.openapi = custom_openapi

# --- deprecated ---


# deprecated: token
@auth_app.get(
    "/token",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": AuthMessage.TOKEN_OKAY,
            "model": ResponseModel[TokenResponse],
        },
    },
    tags=["auth"],
    deprecated=False,
    include_in_schema=False,
)
async def auth(request: Request):
    """
    직접 호출할 일은 없지만 로그인에 성공하면 이곳으로 redirect 됩니다.
    """
    signup_complete = True
    try:
        if not oauth.google:
            raise GoogleModuleError
        logging.debug("request: %s", request)
        access_token = await oauth.google.authorize_access_token(request)
        logging.debug("access_token: %s", access_token)
    except OAuthError as oauth_error:
        # csrf issue or denied by user
        raise CREDENTIALS_EXCEPTION from oauth_error
    logging.debug("access_token: %s", access_token)
    user_data = access_token.get("userinfo")
    if not user_data:
        logging.warning("not user data")
        raise CREDENTIALS_EXCEPTION

    try:
        user_ = UserModel(auth_provider=OAuthProvider.GOOGLE, **user_data)
        user_info = await valid_email_from_db(
            email=user_.email,
            auth_provider=OAuthProvider.GOOGLE,
        )
        if not user_info:
            signup_complete = False
            _okay, user_ = await add_user(user=user_)
            user_info = UserInfo(**user_.model_dump())

    except Exception as user_error:
        logging.exception("user error: %s", user_error)
        raise CREDENTIALS_EXCEPTION from user_error

    access_token_ = create_access_token(
        email=user_info.email, auth_provider=OAuthProvider.GOOGLE
    )
    refresh_token_ = create_refresh_token(
        email=user_info.email, auth_provider=OAuthProvider.GOOGLE
    )
    response_model = TokenResponse(
        access_token=access_token_,
        refresh_token=refresh_token_,
        signup_complete=signup_complete,
    )
    created_at_ = datetime.utcnow()

    await add_token_log(
        payload=TokenLog(
            user_id=user_info.id,
            event_type=EventType.SIGNIN,
            access_token=access_token_,
            refresh_token=refresh_token_,
            grant_type=GrantType.REFRESH_TOKEN,
            created_at=created_at_.strftime("%Y-%m-%d %H:%M:%S"),
            expired_at=(
                created_at_
                + timedelta(
                    minutes=env.app_refresh_token_expire_minutes,
                )
            ).strftime("%Y-%m-%d %H:%M:%S"),
        )
    )
    return custom_response(
        status_code=status.HTTP_200_OK,
        content=ResponseModel[TokenResponse](
            message=AuthMessage.TOKEN_OKAY,
            data=response_model,
        ),
    )


# deprecated: token/signin
@auth_app.post(
    "/token/signin",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": AuthMessage.TOKEN_OKAY,
            "model": ResponseModel[TokenResponse],
        },
    },
    tags=["auth"],
    deprecated=True,
    include_in_schema=False,
)
async def signin(body: IDTokenBody):
    """
    KAKAO 로그인을 추가하면서 각 OAuth Provider 별로 분리하기 위해 deprecate 하기로 결정했습니다.

    ID Token의 무결성을 확인하고 access_token을 발급합니다.
    이 과정에서 사용자가 회원가입되어있지 않으면 DB에 회원정보를 추가합니다.
    """
    users_id_token = body.id_token
    signup_complete = True

    try:
        idinfo = id_token.verify_oauth2_token(
            id_token=users_id_token,
            request=requests.Request(),
            audience=GOOGLE_CLIENT_ID,
        )
        if idinfo["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
            raise ValueError("Wrong issuer.")
        email = idinfo["email"]

        user_info = await valid_email_from_db(
            email=email,
            auth_provider=OAuthProvider.GOOGLE,
        )
        user_ = None
        if not user_info:
            signup_complete = False
            _okay, user_ = await add_user(
                UserModel(
                    auth_provider=OAuthProvider.GOOGLE,
                    **idinfo,
                ),
            )
            user_info = UserInfo(**user_.model_dump())

        access_token_ = create_access_token(
            email=user_info.email, auth_provider=OAuthProvider.GOOGLE
        )
        refresh_token_ = create_refresh_token(
            user_info.email, auth_provider=OAuthProvider.GOOGLE
        )
        response_model = TokenResponse(
            access_token=access_token_,
            refresh_token=refresh_token_,
            signup_complete=signup_complete,
        )
        created_at_ = datetime.now()

        await add_token_log(
            payload=TokenLog(
                user_id=user_info.id,
                event_type=EventType.SIGNIN,
                access_token=access_token_,
                refresh_token=refresh_token_,
                grant_type=GrantType.REFRESH_TOKEN,
                created_at=created_at_.strftime("%Y-%m-%d %H:%M:%S"),
                expired_at=(
                    created_at_
                    + timedelta(
                        minutes=env.app_refresh_token_expire_minutes,
                    )
                ).strftime("%Y-%m-%d %H:%M:%S"),
            )
        )
        return custom_response(
            status_code=status.HTTP_200_OK,
            content=ResponseModel(
                message=AuthMessage.TOKEN_OKAY,
                data=response_model,
            ),
        )
    except ValueError as value_error:
        logging.exception("ValueError: %s", value_error)
        raise CREDENTIALS_EXCEPTION from value_error
    except Exception as credentials_error:
        logging.exception("credentials error: %s", credentials_error)
        raise CREDENTIALS_EXCEPTION from credentials_error
