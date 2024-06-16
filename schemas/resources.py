from typing import Annotated

from pydantic import BaseModel, Field, field_validator

from api.common import generate_hash


class ThemeFields:
    theme_id = Field(
        default_factory=lambda: generate_hash(8),
        description="기본으로 생성되는 테마 ID",
        json_schema_extra={
            "example": "a1b2c3d4",
        },
        min_length=8,
        max_length=8,
    )
    title = Field(
        max_length=64,
        json_schema_extra={"example": "청량하고 산뜻한 청량감 넘치는 분위기로"},
    )
    image_url = Field(
        None,
        max_length=256,
        json_schema_extra={
            "example": "https://github.com/Epson-Innovation-Challenge-Anthology/palm/raw/main/docs/palm-on-palm.jpeg"
        },
    )
    subtitle = Field(
        None,
        max_length=64,
        json_schema_extra={"example": "Description of product"},
    )


class Theme(BaseModel):
    id: Annotated[
        str,
        ThemeFields.theme_id,
    ]
    title: Annotated[
        str,
        ThemeFields.title,
    ]
    subtitle: Annotated[
        str,
        ThemeFields.subtitle,
    ]
    image_url: Annotated[
        str,
        ThemeFields.image_url,
    ]

    @field_validator("image_url")
    def validate_image_url(cls, value):
        if not value.startswith("https://") and not value.startswith("http://"):
            raise ValueError("Image URL must start with 'https://'")
        return value


class ThemeInput(BaseModel):
    title: Annotated[
        str,
        ThemeFields.title,
    ]
    subtitle: Annotated[
        str | None,
        ThemeFields.subtitle,
    ]
    image_url: Annotated[
        str | None,
        ThemeFields.image_url,
    ]


class PictureFields:
    picture_id = Field(
        default_factory=lambda: generate_hash(32),
        description="기본으로 생성되는 사진 ID",
        json_schema_extra={
            "example": "a1b2c3d4e5f6g7h8i9j0a1b2c3d4e5f6",
        },
        min_length=32,
        max_length=64,
    )


class ObjectStorageResponse(BaseModel):
    user_id: str
    picture_id: str
    image_url: str
