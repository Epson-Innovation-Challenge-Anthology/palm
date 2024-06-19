from datetime import datetime

from pydantic import BaseModel, Field

from enums.auth import EventType, GrantType, OAuthProvider, RefreshGrantType
from schemas.users import AuthFields, UserFields


class RefreshBody(BaseModel):
    grant_type: RefreshGrantType = Field(
        json_schema_extra={"example": RefreshGrantType.REFRESH_TOKEN},
        description="토큰 갱신 타입",
    )
    refresh_token: str = Field(
        json_schema_extra={
            "example": "FAKE__ciOiJIUzI1NiIsI....__FAKE",
        },
        description="Refresh Token (Bearer)",
    )


class TokenPayload(BaseModel):
    email: str = Field(
        json_schema_extra={
            "example": "email@email.com",
        },
        description="User ID",
    )
    auth_provider: OAuthProvider = Field(
        json_schema_extra={
            "example": OAuthProvider.GOOGLE,
        },
        description="OAuth Provider",
    )


# pylint: disable=C0301
class RefreshTokenResponse(BaseModel):
    refresh_token: str | None = Field(
        json_schema_extra={
            "example": "FAKE__ciOiJIUzI1NiIsI....XhrD9PJ04CvIqeW4myidWRkdZRDnSTYiOz22f__FAKE",
        },
        description="Refresh Token (Bearer)",
        default=None,
    )
    date: datetime = Field(
        default_factory=datetime.utcnow,
        description="토큰 발급시간",
    )


class AccessTokenResponse(BaseModel):
    access_token: str = Field(
        json_schema_extra={
            "example": "FAKE__ciOiJIPjUSGaNbmYSV31C78cckrCnLXDFqRK98lI4Y__FAKE",
        },
        description="Access Token (Bearer)",
    )


class TokenResponse(RefreshTokenResponse, AccessTokenResponse):
    signup_complete: bool = Field(
        examples=[False, True],
        description="회원가입 프로세스 완료 여부",
    )


class IDTokenBody(BaseModel):
    id_token: str = Field(
        examples=[
            "FAKE__ciOiJIUzI1NiIsI....XhrD9PJ04CvIqeW4myidWRkdZRDnSTYiOz22f__FAKE"
        ],
        description="ID Token (Bearer)",
    )


class KakaoAuthBody(BaseModel):
    code: str = Field(
        examples=[
            "FAKE__ciOiJIUzI1NiIsI....XhrD9PJ04CvIqeW4myidWRkdZRDnSTYiOz22f__FAKE"
        ],
        description="Kakao Auth Code",
    )


class TokenBlacklist(BaseModel):
    token: str  # Unique
    blacklisted_at: datetime = datetime.now()


class TokenLog(BaseModel):
    user_id: str | None = AuthFields.user_id
    event_type: EventType = AuthFields.event_type
    grant_type: GrantType = AuthFields.grant_type
    access_token: str | None = AuthFields.access_token
    refresh_token: str | None = AuthFields.refresh_token
    created_at: str | None = AuthFields.created_at
    expired_at: str | None = AuthFields.expires_in
    blacklisted_at: str | None = AuthFields.blacklisted_at


class SignupBody(BaseModel):
    email: str = UserFields.email
    name: str = UserFields.name
    password: str = UserFields.password
    phone_number: str = UserFields.phone_number
