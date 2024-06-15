from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from api.common import generate_hash
from enums.auth import EventType, GrantType, OAuthProvider
from enums.users import Sex

__all__ = ("UserFields",)


class UserFields:
    user_id = Field(
        default_factory=generate_hash,
        description="기본으로 생성되는 사용자 ID",
        json_schema_extra={"example": "ax10eab"},
    )
    auth_provider = Field(
        description="사용자 인증 제공자",
        examples=[
            OAuthProvider.GOOGLE,
        ],
    )
    email = Field(
        description="사용자 이메일", json_schema_extra={"example": "cocopalm@gmail.com"}
    )
    email_newsfeed = Field(
        default=None,
        description="사용자가 뉴스레터를 구독하기위한 이메일",
        json_schema_extra={"example": "newsfeed@gmail.com"},
    )
    is_active = Field(
        default=True,
        description="사용자 활성화 여부, 탈퇴시 False 전환",
        json_schema_extra={"example": True},
    )
    is_superuser = Field(
        default=False,
        description="사용자의 관리자 권한 여부",
        json_schema_extra={"example": False},
    )
    deactivated_at = Field(
        default=None,
        description="사용자 탈퇴(비활성화) 시점",
        json_schema_extra={"example": "2099-08-17 19:00:00.000000"},
    )
    created_at = Field(
        default_factory=datetime.utcnow,
        description="사용자 생성 시점",
        json_schema_extra={"example": "2021-08-17 19:00:00.000000"},
    )
    updated_at = Field(
        default=None,
        description="사용자 정보 수정 시점",
        json_schema_extra={"example": "2021-08-17 19:00:00.000000"},
    )
    sex = Field(
        default=Sex.OTHER,
        description="사용자 성별",
        examples=[Sex.MALE, Sex.FEMALE, Sex.OTHER],
    )
    name = Field(
        default=None,
        description="사용자 이름",
        json_schema_extra={"example": "코코팜"},
    )
    profile_image_url = Field(
        default=None,
        description="사용자 프로필 사진 URL",
        json_schema_extra={"example": "https://picsum.photos/200/300"},
    )
    allow_notice_email = Field(
        default=False,
        description="주요 공지 관련 이메일 허용 여부",
        json_schema_extra={"example": False},
    )
    allow_event_email = Field(
        default=False,
        description="이벤트관련 이메일 허용 여부",
        json_schema_extra={"example": False},
    )
    bio_links = Field(
        default=[],
        description="사용자 소셜 미디어 링크",
        json_schema_extra={"example": ["https://www.instagram.com/cocopalm/"]},
    )
    bio = Field(
        default=None,
        description="사용자 소개 문구",
        json_schema_extra={"example": "코코팜 맛있다."},
    )


class AuthFields:
    user_id = Field(
        description="사용자 ID",
        json_schema_extra={"example": "ax10eab"},
        default=None,
    )
    grant_type = Field(
        default=GrantType.ACCESS_TOKEN,
        description="토큰 발급 타입",
        examples=[GrantType.ACCESS_TOKEN, GrantType.REFRESH_TOKEN],
    )
    created_at = Field(
        default=None,
        description="토큰 발급 시점",
        json_schema_extra={"example": "2024-04-04 19:00:00.000000"},
    )
    expires_in = Field(
        default=None,
        description="토큰 만료 예정 시간",
        json_schema_extra={"example": "2024-06-04 19:00:00.000000"},
    )
    blacklisted_at = Field(
        default=None,
        description="토큰이 블랙리스트에 등록된 시점",
        json_schema_extra={"example": "2024-04-04 19:00:00.000000"},
    )
    refresh_token = Field(
        default=None,
        description="refresh token",
        json_schema_extra={"example": "FAKE__ciOiJIUzI1Ni__FAKE"},
    )
    access_token = Field(
        default=None,
        description="access token",
        json_schema_extra={
            "example": "FAKE__ciOiJIUzI1NiIsI....XkdZRDnSTYiOz22f__FAKE",
        },
    )
    event_type = Field(
        description="이벤트 타입",
        examples=[
            EventType.SIGNIN,
            EventType.SIGNOUT,
            EventType.BLACKLIST,
            EventType.REFRESH_ACCESS_TOKEN,
        ],
    )


class UserModel(BaseModel):
    id: str = UserFields.user_id
    name: str | None = UserFields.name
    auth_provider: OAuthProvider = UserFields.auth_provider
    email: EmailStr = UserFields.email
    service_email: EmailStr | None = UserFields.service_email
    is_active: bool = UserFields.is_active
    is_superuser: bool = UserFields.is_superuser
    deactivated_at: Optional[datetime] = UserFields.deactivated_at
    created_at: datetime = UserFields.created_at
    updated_at: datetime | None = UserFields.updated_at
    bio_links: list[str] = UserFields.bio_links
    sex: Optional[Sex] = UserFields.sex
    profile_image_url: str | None = UserFields.profile_image_url
    bio: str | None = UserFields.bio

    @field_validator("id", mode="before")
    def validate_id(cls, v):
        return str(v)

    @field_validator("deactivated_at", mode="before")
    def validate_deactivated_at(cls, v):
        if v is None:
            return v
        try:
            # is v datetime?
            datetime.strptime(str(v), "%Y-%m-%d %H:%M:%S.%f")
        except ValueError as incorrect_date_format:
            raise ValueError(
                "Incorrect data format, should be YYYY-MM-DD HH:MM:SS.mmmmmm"
            ) from incorrect_date_format
        return v


class UserInfo(BaseModel):
    id: str = UserFields.user_id
    name: str | None = UserFields.name
    auth_provider: OAuthProvider = UserFields.auth_provider
    email: EmailStr = UserFields.email
    service_email: EmailStr | None = UserFields.service_email
    is_active: bool = UserFields.is_active
    is_superuser: bool = UserFields.is_superuser
    created_at: datetime = UserFields.created_at
    deactivated_at: datetime | None = UserFields.deactivated_at
    updated_at: datetime | None = UserFields.updated_at
    bio_links: list[str] = UserFields.bio_links
    sex: Optional[Sex] = UserFields.sex
    profile_image_url: str | None = UserFields.profile_image_url
    bio: str | None = UserFields.bio
