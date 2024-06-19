from datetime import datetime
from random import randint

from fastapi import APIRouter, Body, File, UploadFile, status

from api.epson import Epson
from api.messages import MESSAGES
from api.settings import env
from responses.common import custom_response
from schemas import ResponseModel

router = APIRouter(prefix="/epson", tags=["epson"])


@router.post(
    "/print",
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        status.HTTP_202_ACCEPTED: {
            "description": MESSAGES.PRINT_ACCEPTED,
        },
    },
)
async def ask_something(
    upload_file: UploadFile = File(...),
):
    """
    파일기반 프린터 요청

    NOTE: 아마 직접적으로 파일 올리는방식은 안쓰일것같음..
    """
    return custom_response(
        status_code=status.HTTP_202_ACCEPTED,
        content=ResponseModel[None](
            message=MESSAGES.PRINT_ACCEPTED,
            data=None,
        ),
    )
