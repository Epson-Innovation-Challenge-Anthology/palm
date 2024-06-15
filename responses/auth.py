from pydantic import BaseModel

from enums.auth import AuthMessage
from schemas.auth import AccessTokenResponse, TokenResponse


class LogoutOkay(BaseModel):
    message: str = AuthMessage.LOGOUT_SUCCESS


class TokenOkay(BaseModel):
    message: str = AuthMessage.TOKEN_OKAY
    data: TokenResponse


class TokenRefreshOkay(BaseModel):
    message: str = AuthMessage.TOKEN_REFRESH_OKAY
    data: AccessTokenResponse
