from fastapi import APIRouter, Body, status

from api.chat import services as chat_services
from api.messages import MESSAGES
from responses.common import custom_response
from schemas import ResponseModel
from schemas.chat import AskBody, AskResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post(
    "/ask",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": MESSAGES.CHAT_ASK_SUCCESS,
            "model": ResponseModel[AskResponse].inject(
                message=MESSAGES.CHAT_ASK_SUCCESS,
                data=AskResponse,
            ),
        },
    },
)
async def ask_something(
    body: AskBody = Body(...),
):
    """
    메시지 입력
    """
    response = await chat_services.ask_something(body=body)
    return custom_response(
        status_code=status.HTTP_200_OK,
        content=ResponseModel(
            message=MESSAGES.CHAT_ASK_SUCCESS,
            data=AskResponse(content=response),
        ),
    )
