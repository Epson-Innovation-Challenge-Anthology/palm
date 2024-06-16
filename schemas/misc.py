from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field


class MailFields:
    family_name = Field(
        description="성", json_schema_extra={"example": "팜"}, min_length=1
    )
    given_name = Field(
        description="이름", json_schema_extra={"example": "코코"}, min_length=1
    )
    author_email = Field(
        description="이메일",
        pattern=r"^([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)$",
        min_length=5,
        json_schema_extra={"example": "coco@p.alm"},
    )
    content = Field(
        description="내용",
        min_length=10,
        json_schema_extra={"example": "ㅎㅇㅎㅇ 코코팜 맛있다"},
    )
    created_at = Field(
        deprecated=True,
        description="생성 시점",
        json_schema_extra={"example": "2024-06-10 19:00:00.000000"},
        default_factory=datetime.now,
    )


class MailContent(BaseModel):
    family_name: Annotated[str, MailFields.family_name]
    given_name: Annotated[str, MailFields.given_name]
    author_email: Annotated[str, MailFields.author_email]
    content: Annotated[str, MailFields.content]
    created_at: Annotated[datetime, MailFields.created_at]
