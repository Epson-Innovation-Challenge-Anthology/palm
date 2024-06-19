from pydantic import BaseModel


class AskBody(BaseModel):
    content: str


class AskResponse(BaseModel):
    content: str | None  # 응답이 없을 수도 있음
