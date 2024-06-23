import logging
import os
from datetime import datetime

from fastapi import APIRouter, File, UploadFile, status

from api.common import generate_hash
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

    NOTE: pdf 파일을 업로드해주세요.
    """
    async with Epson(
        client_id=env.epson_client_id,
        secret=env.epson_client_secret,
        device_id=env.epson_email_id,
        handle_id=datetime.now().strftime("%Y%m%d%H%M%S"),
    ) as epson:
        if not upload_file.filename:
            return custom_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=ResponseModel[None](
                    message=MESSAGES.PRINT_FILE_NOT_FOUND,
                    data=None,
                ),
            )
        # save file to local
        file_extension = upload_file.filename.split(".")[-1]
        file_path = f"{generate_hash()}.{file_extension}"
        logging.info("file_path = %s", file_path)
        with open(file_path, "wb") as f:
            f.write(upload_file.file.read())
        # is exist file
        if not os.path.exists(file_path):
            return custom_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=ResponseModel[None](
                    message=MESSAGES.PRINT_FILE_NOT_FOUND,
                    data=None,
                ),
            )
        await epson.print_file_by_path(file_path=file_path)

    return custom_response(
        status_code=status.HTTP_202_ACCEPTED,
        content=ResponseModel[None](
            message=MESSAGES.PRINT_ACCEPTED,
            data=None,
        ),
    )
