from datetime import datetime

from pydantic import BaseModel, Field

from api.common import generate_hash
from enums.orbit import DistanceType


class OrbitFields:
    distance: DistanceType = Field(
        json_schema_extra={"example": DistanceType.CLOSER},
        description="관계의 거리",
    )
    from_user_id: str = Field(
        json_schema_extra={
            "example": "...",
        },
        description="사용자 ID",
    )
    to_user_id: str = Field(
        json_schema_extra={
            "example": "...",
        },
        description="사용자 ID",
    )
    user_profile_image: str = Field(
        json_schema_extra={
            "example": "...",
        },
        description="프로필 이미지",
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        description="업데이트 일자",
    )
    foot_print_title: str = Field(
        json_schema_extra={
            "example": "활동 기록명",
        },
        description="활동 기록명",
    )
    friend_name: str = Field(
        json_schema_extra={
            "example": "...",
        },
        description="친구 이름",
    )
    foot_print_id: str = Field(
        json_schema_extra={
            "example": "...",
        },
        description="활동 기록 ID",
        default_factory=generate_hash,
    )


class FootPrintBody(BaseModel):
    title: str = OrbitFields.foot_print_title
    image_url: str | None = Field(
        json_schema_extra={
            "example": None,
        },
        description="이미지 URL",
    )


class FootPrintModel(BaseModel):
    id: str = OrbitFields.foot_print_id
    title: str = OrbitFields.foot_print_title
    image_url: str | None = Field(
        json_schema_extra={
            "example": None,
        },
        description="이미지 URL",
    )
    updated_at: datetime = OrbitFields.updated_at


class OrbitModel(BaseModel):
    distance: DistanceType = OrbitFields.distance
    from_user_id: str = OrbitFields.from_user_id
    to_user_id: str = OrbitFields.to_user_id
    updated_at: datetime = OrbitFields.updated_at
    foot_prints: list[FootPrintModel] = Field(
        default_factory=list,
        description="Foot prints",
    )


class OrbitInfo(BaseModel):
    distance: DistanceType = OrbitFields.distance
    user_id: str = OrbitFields.to_user_id
    user_profile_image: str = OrbitFields.user_profile_image
    friend_name: str = OrbitFields.friend_name
    updated_at: datetime = OrbitFields.updated_at
    foot_prints: list[FootPrintModel] = Field(
        default_factory=list,
        description="Foot prints",
    )
