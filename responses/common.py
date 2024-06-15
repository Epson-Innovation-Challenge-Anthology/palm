from typing import Annotated, Generic, TypeVar

from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel, Field

T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    message: Annotated[
        str | None,
        Field(None, title="Message", description="Response message"),
    ]
    data: T


class Unauthorized(BaseModel):
    detail: str = "Not authenticated"


def custom_response(
    content: ResponseModel[T],
    status_code: int = status.HTTP_200_OK,
) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=status_code,
        content=jsonable_encoder(content),
    )
