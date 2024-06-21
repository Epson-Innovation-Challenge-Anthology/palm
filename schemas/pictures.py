from datetime import datetime

from pydantic import BaseModel, Field


class PictureFields:
    picture_ids = Field(
        default=[],
        description="업로드된 사진 ID 목록",
        json_schema_extra={"example": ["6qerhu4sd1vt1bh3"]},
    )
    picture_urls = Field(
        default=[],
        description="업로드된 사진 URL 목록",
        json_schema_extra={"example": ["https://www.example.com/6qerhu4sd1vt1bh3"]},
    )


class PictureMetaModel(BaseModel):
    # UserFields 별도 파일로 분리
    user_id: str = Field(
        description="사용자 ID",
        json_schema_extra={"example": "6qerhu4sd1vt1bh3"},
    )
    ids: list[str] = PictureFields.picture_ids
    modified_at: datetime = Field(
        description="최근 수정 시간",
        json_schema_extra={"example": "2024-08-17 19:00:00.000000"},
    )


class PictureMetaInfo(BaseModel):
    user_id: str = Field(
        description="사용자 ID",
        json_schema_extra={"example": "6qerhu4sd1vt1bh3"},
    )
    urls: list[str] = PictureFields.picture_urls
    modified_at: datetime = Field(
        description="최근 수정 시간",
        json_schema_extra={"example": "2024-08-17 19:00:00.000000"},
    )
