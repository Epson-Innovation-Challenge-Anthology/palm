import logging

from async_lru import alru_cache  # lru_cache for async

from api.db.persistant import mongo
from schemas.resources import Theme, ThemeInput


@alru_cache(maxsize=128)
async def get_theme_resources() -> list[Theme]:
    """
    촬영테마 정보를 가져올 때 사용해요
    """
    theme_resources = await mongo.theme.find().to_list(None)
    return [Theme(**theme) for theme in theme_resources]


async def add_theme_resources(themes: list[ThemeInput]) -> tuple[bool, list[Theme]]:
    """
    촬영테마 정보를 추가할 때 사용해요
    """
    new_themes = [Theme(**theme.model_dump()) for theme in themes]
    resp = await mongo.theme.insert_many([theme.model_dump() for theme in new_themes])
    logging.debug("add theme resp -> %s", resp)
    return resp.acknowledged, new_themes or []


async def remove_theme(theme_id: str) -> bool:
    """
    촬영테마 정보를 삭제할 때 사용해요
    """
    resp = await mongo.theme.delete_one({"_id": theme_id})
    return resp.acknowledged


async def update_theme(theme_id: str, theme: ThemeInput) -> bool:
    """
    촬영테마 정보를 수정할 때 사용해요
    """
    resp = await mongo.theme.update_one({"_id": theme_id}, {"$set": theme.model_dump()})
    return resp.acknowledged
