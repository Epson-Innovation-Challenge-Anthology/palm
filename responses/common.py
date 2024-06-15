from typing import Annotated, Generic, Optional, TypeVar

from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel, Field, create_model

T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    message: Annotated[
        str | None,
        Field(
            "응답 안내메시지 예시",
            title="Message",
            description="Response message",
        ),
    ]
    data: T | bool | None = None

    def __init__(self, message: str, data: T):
        super().__init__(message=message, data=data)

    @classmethod
    def inject(cls, message: str, data: type[T] | None = None) -> type[T]:
        fields = {
            "message": (str, Field(message)),
            "data": (data, Field(...)),
        }

        return create_model(  # type: ignore
            "Response" + cls.__name__,
            **fields,
        )


class ResponseExample(ResponseModel):
    class Config:
        arbitrary_types_allowed = True


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


class BaseModelFactory:
    @classmethod
    def nullable(cls, model: type[T]) -> type[T]:
        """
        BaseModel을 상속받은 클래스의 필드를 모두 Optional 타입으로 변경한 새로운 클래스를 반환합니다.

        Optional 타입으로 변경된 필드의 기본값은 None으로 변경됩니다.
        """
        new_fields = {}
        for name, field in model.__annotations__.items():
            new_fields[name] = (Optional[field], Field(default=None))
        return create_model("Nullable" + model.__name__, **new_fields)
