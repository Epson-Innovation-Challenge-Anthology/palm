from enum import Enum


class GrantType(str, Enum):
    REFRESH_TOKEN = "refresh_token"
    ACCESS_TOKEN = "access_token"


class RefreshGrantType(str, Enum):
    REFRESH_TOKEN = "refresh_token"


class AuthMessage(str, Enum):
    LOGOUT_SUCCESS = "로그아웃 되었습니다"
    TOKEN_OKAY = "토큰이 발급되었습니다"
    TOKEN_REFRESH_OKAY = "토큰이 갱신되었습니다"
    TOKEN_BLACKLISTED = "토큰이 블랙리스트에 등록되었습니다"


class EventType(str, Enum):
    SIGNIN = "signin"
    SIGNOUT = "signout"
    BLACKLIST = "blacklist"
    REFRESH_ACCESS_TOKEN = "refresh_access_token"


class OAuthProvider(str, Enum):
    GOOGLE = "google"
    KAKAO = "kakao"
