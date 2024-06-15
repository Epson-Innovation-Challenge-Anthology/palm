import logging
from collections import defaultdict
from typing import Annotated

import orjson
from aiohttp import ClientSession
from fastapi import APIRouter, BackgroundTasks, Depends, Path, Query, status
from fastapi.responses import ORJSONResponse

from api.db.implements.mongo import get_user_by_email, ping
from api.db.persistant import mongo
from api.jwt import get_current_user_email_bearer
from api.settings import env
from responses.common import custom_response
from schemas import ResponseModel
from schemas.users import UserInfo

router = APIRouter(prefix="/users", tags=["user"])


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": "사용자 정보 조회 성공",
            "model": ResponseModel[UserInfo],
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "사용자 정보가 존재하지 않음",
            "model": ResponseModel[None],
        },
    },
)
async def get_my_profile(
    token_payload=Depends(get_current_user_email_bearer),
):
    """
    로그인한 사용자가 내 정보를 가져올 때 사용해요
    """
    user_info = await get_user_by_email(
        email=token_payload.email,
        auth_provider=token_payload.auth_provider,
    )
    if user_info:
        return custom_response(
            status_code=status.HTTP_200_OK,
            content=ResponseModel[UserInfo](
                message="사용자 정보를 조회합니다.",
                data=UserInfo(**user_info.model_dump()),
            ),
        )
    return custom_response(
        status_code=status.HTTP_404_NOT_FOUND,
        content=ResponseModel[None](
            message="사용자 정보를 찾을 수 없습니다.",
            data=None,
        ),
    )
