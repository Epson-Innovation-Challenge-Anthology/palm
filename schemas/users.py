import logging
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from api.common import generate_hash
from enums.auth import EventType, GrantType, OAuthProvider
from enums.users import Plan, Sex

__all__ = ("UserFields",)


class UserFields:
    user_id = Field(
        description="기본으로 생성되는 사용자 ID",
        json_schema_extra={
            "example": "6qerhu4sd1vt1bh3",
        },
        min_length=8,
        max_length=16,
        default_factory=generate_hash,
        pattern="^[a-zA-Z0-9]*$",
    )
    auth_provider = Field(
        description="사용자 인증 제공자",
        examples=[
            OAuthProvider.GOOGLE,
        ],
    )
    password = Field(
        default=None,
        description="사용자 비밀번호",
        json_schema_extra={"example": "Qwer1234!!"},
        min_length=8,
    )
    hashed_password = Field(
        description="해시된 사용자 비밀번호",
        json_schema_extra={"example": "190cxzv239we98f9dsv98asd9..."},
    )
    phone_number = Field(
        default=None,
        description="사용자 전화번호",
        json_schema_extra={"example": "010-1234-5678"},
    )
    email = Field(
        description="사용자 이메일",
        json_schema_extra={"example": "cocopalm@gmail.com"},
    )
    service_email = Field(
        default=None,
        description="사용자가 서비스에 사용할 이메일, 가입 직후 email과 동일",
        json_schema_extra={"example": "cocopalm@gmail.com"},
        min_length=5,
        pattern=r"^([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)$",
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
        default_factory=datetime.now,
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
        max_length=16,
    )
    profile_image = Field(
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
    urls = Field(
        default=[],
        description="사용자 소셜 미디어 링크",
        json_schema_extra={"example": ["https://www.instagram.com/cocopalm/"]},
    )
    bio = Field(
        default=None,
        description="사용자 소개 문구",
        json_schema_extra={"example": "코코팜 맛있다."},
    )
    using_plan = Field(
        default=Plan.BASIC,
        description="사용중인 서비스 플랜",
        examples=[Plan.BASIC, Plan.BEGINNER, Plan.EXPERT, Plan.MASTER],
    )
    plan_expired_at = Field(
        default=None,
        description="서비스 플랜 만료 시점",
        json_schema_extra={"example": "2024-08-17 19:00:00.000000"},
    )
    auto_subscription = Field(
        default=False,
        description="플랜 만료시점의 자동 결제 여부",
        json_schema_extra={"example": False},
    )


class AuthFields:
    user_id = Field(
        description="사용자 ID",
        json_schema_extra={"example": "6qerhu4sd1vt1bh3"},
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
    password: str | None = UserFields.hashed_password
    phone_number: str | None = None
    is_active: bool = UserFields.is_active
    is_superuser: bool = UserFields.is_superuser
    deactivated_at: Optional[datetime] = UserFields.deactivated_at
    created_at: datetime = UserFields.created_at
    updated_at: datetime | None = UserFields.updated_at
    urls: list[str] = UserFields.urls
    sex: Optional[Sex] = UserFields.sex
    profile_image: str | None = UserFields.profile_image
    bio: str | None = UserFields.bio
    plan_expired_at: Optional[datetime] = UserFields.plan_expired_at
    using_plan: Plan = UserFields.using_plan
    auto_subscription: bool = UserFields.auto_subscription

    @field_validator("id", mode="before")
    def validate_id(cls, v):
        if v is None:
            raise ValueError("고유식별값은 필수 입력값입니다.")
        if len(v) < 8:
            raise ValueError("고유식별값은 최소 8자리 이상 입력해주세요.")
        if len(v) > 17:
            raise ValueError("고유식별값은 최대 16자리 이하로 입력해주세요.")
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

    @field_validator("using_plan", mode="before")
    def validate_using_plan(cls, value, values, **kwargs):
        print(f"{values = }")
        print(f"{kwargs = }")

        if value is None:
            return Plan.BASIC
        if value not in Plan.__members__:
            logging.exception("Plan이 잘못 입력되었습니다.: %s", value)
            return Plan.BASIC
        plan_expired_at = values.data.get("plan_expired_at", None)
        if plan_expired_at is None:
            return Plan.BASIC
        if plan_expired_at < datetime.now():
            return Plan.BASIC
        return value


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
    urls: list[str] = UserFields.urls
    sex: Optional[Sex] = UserFields.sex
    profile_image: str | None = UserFields.profile_image
    bio: str | None = UserFields.bio
    # 순서 영향받음
    plan_expired_at: Optional[datetime] = UserFields.plan_expired_at
    using_plan: Plan = UserFields.using_plan
    auto_subscription: bool = UserFields.auto_subscription

    @field_validator("using_plan", mode="before")
    def validate_using_plan(cls, value, values, **kwargs):
        print(f"{values = }")
        print(f"{kwargs = }")

        if value is None:
            return Plan.BASIC
        if value not in Plan.__members__:
            logging.exception("Plan이 잘못 입력되었습니다.: %s", value)
            return Plan.BASIC
        plan_expired_at = values.data.get("plan_expired_at", None)
        if plan_expired_at is None:
            return Plan.BASIC
        if plan_expired_at < datetime.now():
            return Plan.BASIC
        return value


class PatchableUserInfo(BaseModel):
    id: str | None = UserFields.user_id
    name: str | None = UserFields.name
    service_email: EmailStr | None = UserFields.service_email
    urls: list[str] | None = UserFields.urls

    @field_validator("urls", mode="before")
    def validate_urls(cls, v):
        if v is None:
            return v
        for url in v:
            if not url.startswith("http"):
                raise ValueError("URL은 http 또는 https로 시작해야합니다.")
        return v


class UserProfileImage(BaseModel):
    profile_image: str = UserFields.profile_image
