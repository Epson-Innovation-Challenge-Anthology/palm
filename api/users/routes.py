from typing import Annotated

from fastapi import APIRouter, Body, Depends, status

from api.db.implements.mongo import (
    get_user_by_email,
    patch_user_by_email,
    patch_user_profile_image,
)
from api.jwt import get_current_user_email_bearer
from responses.common import custom_response
from schemas import ResponseModel
from schemas.users import PatchableUserInfo, UserInfo, UserProfileImage

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


@router.patch(
    "/me",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": "사용자 정보 수정 성공",
            "model": ResponseModel[UserInfo].inject(
                message="사용자 정보를 수정 성공",
                data=UserInfo,
            ),
        },
    },
)
async def update_my_profile(
    user_info: PatchableUserInfo,
    token_payload=Depends(get_current_user_email_bearer),
):
    """
    로그인한 사용자가 내 정보를 수정할 때 사용해요
    """
    okay, user_info_ = await patch_user_by_email(
        email=token_payload.email,
        auth_provider=token_payload.auth_provider,
        user_info=user_info,
    )
    if not user_info_:
        return custom_response(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ResponseModel[None](
                message="사용자 정보를 찾을 수 없습니다.",
                data=None,
            ),
        )
    if not okay:
        return custom_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ResponseModel[None](
                message="사용자 정보를 수정하지 못했습니다. 관리자에게 문의하세요.",
                data=None,
            ),
        )

    return custom_response(
        status_code=status.HTTP_200_OK,
        content=ResponseModel[UserInfo](
            message="사용자 정보를 수정합니다.",
            data=user_info_,
        ),
    )


@router.patch(
    "/me/profile-image",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": "프로필 이미지 수정 성공",
            "model": ResponseModel[UserInfo].inject(
                message="프로필 이미지 수정 성공",
                data=UserInfo,
            ),
        },
    },
)
async def update_my_profile_image(
    body: Annotated[
        UserProfileImage, Body(description="프로필 이미지 수정을 위한 정보 입력")
    ],
    token_payload=Depends(get_current_user_email_bearer),
):
    """
    로그인한 사용자가 프로필 이미지를 수정할 때 사용해요
    """
    okay, user_info = await patch_user_profile_image(
        email=token_payload.email,
        auth_provider=token_payload.auth_provider,
        profile_image=body.profile_image,
    )
    if not user_info:
        return custom_response(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ResponseModel[None](
                message="사용자 정보를 찾을 수 없습니다.",
                data=None,
            ),
        )
    if not okay:
        return custom_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ResponseModel[None](
                message="사용자 정보를 수정하지 못했습니다. 관리자에게 문의하세요.",
                data=None,
            ),
        )
    return custom_response(
        status_code=status.HTTP_200_OK,
        content=ResponseModel[UserInfo](
            message="사용자 정보를 수정합니다.",
            data=user_info,
        ),
    )
