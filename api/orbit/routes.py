from typing import Annotated

from fastapi import APIRouter, Body, Depends, status
from pydantic import Field

from api.jwt import get_current_user_bearer
from api.messages import MESSAGES
from api.orbit import services
from enums.orbit import DistanceType
from responses.common import custom_response
from schemas import ResponseModel
from schemas.orbit import FootPrintBody, OrbitInfo
from schemas.users import UserInfo

router = APIRouter(prefix="/orbit", tags=["orbit"])


@router.put(
    "/{to_user_id}/distance/{distance}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": MESSAGES.USER_ON_TRACK,
        },
    },
)
async def keep_user_on_track(
    distance: Annotated[DistanceType, "관계의 거리"],
    to_user_id: Annotated[str, "사용자 ID"],
    user_info: UserInfo = Depends(get_current_user_bearer),
):
    """
    로그인한 사용자가 프로필 이미지를 수정할 때 사용해요
    """
    from_user_id = user_info.id
    _ = await services.keep_user_on_track(from_user_id, to_user_id, distance)

    return custom_response(
        status_code=status.HTTP_200_OK,
        content=ResponseModel[None](
            message=MESSAGES.USER_ON_TRACK,
            data=None,
        ),
    )


@router.delete(
    "/{to_user_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": MESSAGES.USER_GOT_OFF_TRACK,
        },
    },
)
async def kick_user_off_track(
    to_user_id: str,
    user_info: UserInfo = Depends(get_current_user_bearer),
):
    """
    로그인한 사용자가 프로필 이미지를 수정할 때 사용해요
    """
    from_user_id = user_info.id
    _ = await services.kick_user_off_track(from_user_id, to_user_id)

    return custom_response(
        status_code=status.HTTP_200_OK,
        content=ResponseModel[None](
            message=MESSAGES.USER_GOT_OFF_TRACK,
            data=None,
        ),
    )


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": MESSAGES.GOT_ORBIT_LOGS,
            "model": ResponseModel[list[OrbitInfo]].inject(
                message=MESSAGES.GOT_ORBIT_LOGS,
                data=list[OrbitInfo],
            ),
        },
    },
)
async def get_user_orbit_info_list(
    user_info: UserInfo = Depends(get_current_user_bearer),
):
    """
    로그인한 사용자가 프로필 이미지를 수정할 때 사용해요
    """
    user_id = user_info.id
    orbit_info_list = await services.get_user_orbit_info(user_id)

    return custom_response(
        status_code=status.HTTP_200_OK,
        content=ResponseModel[list[OrbitInfo]](
            message=MESSAGES.GOT_ORBIT_LOGS,
            data=orbit_info_list,
        ),
    )


@router.put(
    "/{to_user_id}/foot-print",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": MESSAGES.FOOT_PRINT_CREATED,
        },
    },
)
async def create_foot_print(
    to_user_id: str,
    foot_print: FootPrintBody = Body(...),
    user_info: UserInfo = Depends(get_current_user_bearer),
):
    """
    로그인한 사용자가 프로필 이미지를 수정할 때 사용해요
    """
    from_user_id = user_info.id
    _ = await services.add_foot_print(from_user_id, to_user_id, foot_print)

    return custom_response(
        status_code=status.HTTP_200_OK,
        content=ResponseModel[None](
            message=MESSAGES.FOOT_PRINT_CREATED,
            data=None,
        ),
    )


@router.delete(
    "/{to_user_id}/foot-print/{foot_print_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": MESSAGES.FOOT_PRINT_REMOVE_SUCCESS,
        },
    },
)
async def remove_foot_print(
    to_user_id: str,
    foot_print_id: str,
    user_info: UserInfo = Depends(get_current_user_bearer),
):
    """
    로그인한 사용자가 프로필 이미지를 수정할 때 사용해요
    """
    from_user_id = user_info.id
    _ = await services.remove_foot_print(from_user_id, to_user_id, foot_print_id)

    return custom_response(
        status_code=status.HTTP_200_OK,
        content=ResponseModel[None](
            message=MESSAGES.FOOT_PRINT_REMOVE_SUCCESS,
            data=None,
        ),
    )
