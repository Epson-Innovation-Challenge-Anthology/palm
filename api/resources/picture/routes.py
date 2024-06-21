from fastapi import APIRouter, Depends, File, UploadFile, status

from api.common import generate_hash
from api.db.implements.mongo import get_user_by_email
from api.jwt import get_current_user_email_bearer
from api.messages import MESSAGES
from api.resources import services as resource_services
from responses.common import custom_response
from schemas import ResponseModel
from schemas.resources import ObjectStorageResponse

router = APIRouter(prefix="/picture")


@router.post(
    "",
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        status.HTTP_202_ACCEPTED: {
            "description": MESSAGES.PICTURE_UPLOADING,
            "model": ResponseModel[ObjectStorageResponse].inject(
                message=MESSAGES.PICTURE_UPLOADING,
                data=ObjectStorageResponse,
            ),
        },
    },
)
async def upload_picture(
    file: UploadFile = File(...),
    token_payload=Depends(get_current_user_email_bearer),
):
    """
    사진 업로드할 때 사용해요
    """
    user_info = await get_user_by_email(
        email=token_payload.email,
        auth_provider=token_payload.auth_provider,
    )
    if not user_info:
        return custom_response(
            status_code=status.HTTP_403_FORBIDDEN,
            content=ResponseModel[None](
                message=MESSAGES.FORBIDDEN,
                data=None,
            ),
        )
    if not file.content_type:
        return custom_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ResponseModel[bool](
                message=MESSAGES.PICTURE_WRONG_FORMAT,
                data=False,
            ),
        )
    if file.content_type.split("/")[0] != "image":
        return custom_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ResponseModel[bool](
                message=MESSAGES.PICTURE_WRONG_FORMAT,
                data=False,
            ),
        )
    extension = file.content_type.split("/")[-1]
    okay, response = await resource_services.upload_picture(
        user_id=user_info.id,
        filename=f"{generate_hash(32)}.{extension}",
        file=file,
    )
    if not okay:
        return custom_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ResponseModel[bool](
                message=MESSAGES.PICTURE_UPLOAD_FAIL,
                data=False,
            ),
        )
    if not response:
        return custom_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ResponseModel[bool](
                message=MESSAGES.PICTURE_UPLOAD_FAIL,
                data=False,
            ),
        )
    return custom_response(
        status_code=status.HTTP_202_ACCEPTED,
        content=ResponseModel[ObjectStorageResponse](
            message=MESSAGES.PICTURE_UPLOADING,
            data=ObjectStorageResponse(
                user_id=user_info.id,
                picture_id=response.picture_id,
                image_url=response.image_url,
            ),
        ),
    )
