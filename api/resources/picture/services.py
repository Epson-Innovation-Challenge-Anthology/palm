import logging

from api.db.persistant import mongo as db
from schemas.pictures import PictureMetaModel


async def get_user_picture_meta(user_id: str) -> tuple[bool, PictureMetaModel | None]:
    print("user_id = ", user_id)
    try:
        meta_from_db = await db.picture_meta.find_one(
            {
                "user_id": user_id,
            }
        )
        if meta_from_db is None:
            return False, None
        return True, PictureMetaModel(**meta_from_db)
    except Exception as e:
        logging.exception("Error while getting user picture meta: %s", e)
        return False, None
