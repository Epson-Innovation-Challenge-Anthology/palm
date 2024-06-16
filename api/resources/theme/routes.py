from typing import Annotated

from fastapi import APIRouter, Body, Path, status

from api.messages import MESSAGES
from api.resources import services as resource_services
from responses.common import custom_response
from schemas import ResponseModel
from schemas.resources import Theme, ThemeInput

router = APIRouter(prefix="/theme")


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": MESSAGES.GOT_THEME,
            "model": ResponseModel[list[Theme]].inject(
                message=MESSAGES.GOT_THEME,
                data=list[Theme],
            ),
        },
        status.HTTP_404_NOT_FOUND: {
            "description": MESSAGES.THEME_NOT_FOUND,
            "model": ResponseModel[list[None]].inject(
                message=MESSAGES.THEME_NOT_FOUND,
                data=list[None],
            ),
        },
    },
)
async def get_theme_resources():
    """
    촬영테마 정보를 가져올 때 사용해요
    """
    theme_resources = await resource_services.get_theme_resources()
    if theme_resources:
        return custom_response(
            status_code=status.HTTP_200_OK,
            content=ResponseModel[list[Theme]](
                message=MESSAGES.GOT_THEME,
                data=theme_resources,
            ),
        )
    return custom_response(
        status_code=status.HTTP_404_NOT_FOUND,
        content=ResponseModel[list](
            message=MESSAGES.THEME_NOT_FOUND,
            data=[],
        ),
    )


@router.put(
    "",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "description": MESSAGES.THEME_CREATED,
            "model": ResponseModel[list[Theme]].inject(
                message=MESSAGES.THEME_CREATED,
                data=list[Theme],
            ),
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": MESSAGES.THEME_REQUIRED,
            "model": ResponseModel[list[None]].inject(
                message=MESSAGES.THEME_REQUIRED,
                data=list[None],
            ),
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": MESSAGES.THEME_ERROR_WHILE_ADDING,
            "model": ResponseModel[list[None]].inject(
                message=MESSAGES.THEME_ERROR_WHILE_ADDING,
                data=list[None],
            ),
        },
    },
)
async def add_theme_resources(
    themes: Annotated[list[ThemeInput], Body(...)],
):
    """
    촬영테마 정보를 추가할 때 사용해요
    """
    if not themes:
        return custom_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ResponseModel[list](
                message=MESSAGES.THEME_REQUIRED,
                data=[],
            ),
        )
    okay, resp_themes = await resource_services.add_theme_resources(themes)
    if not okay:
        return custom_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ResponseModel[list](
                message=MESSAGES.THEME_ERROR_WHILE_ADDING,
                data=[],
            ),
        )
    return custom_response(
        status_code=status.HTTP_201_CREATED,
        content=ResponseModel[list[Theme]](
            message=MESSAGES.THEME_CREATED,
            data=resp_themes,
        ),
    )


@router.delete(
    "/{theme_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": MESSAGES.THEME_REMOVE_SUCCESS,
            "model": ResponseModel[bool],
        }
    },
)
async def remove_theme(
    theme_id: Annotated[str, Path(..., title="테마 ID", min_length=8, max_length=8)],
):
    """
    촬영테마 정보를 삭제할 때 사용해요
    """
    _ = await resource_services.remove_theme(theme_id)
    return custom_response(
        status_code=status.HTTP_200_OK,
        content=ResponseModel[bool](
            message=MESSAGES.THEME_REMOVE_SUCCESS,
            data=True,
        ),
    )
