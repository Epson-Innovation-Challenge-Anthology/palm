import logging
from datetime import datetime, timedelta

from pymongo import ReturnDocument

from api.db.persistant import mongo as db
from enums.auth import OAuthProvider
from enums.orbit import DistanceType
from enums.users import Plan
from schemas.auth import TokenLog
from schemas.orbit import FootPrintBody, FootPrintModel, OrbitModel
from schemas.users import PatchableUserInfo, UserInfo, UserModel


async def get_user_by_email(
    email: str,
    auth_provider: OAuthProvider,
) -> UserModel | None:
    try:
        user_from_db = await db.users.find_one(
            {
                "email": email,
                "auth_provider": auth_provider,
            }
        )
        if user_from_db is None:
            return None
    except Exception as e:
        raise e
    user_model = UserModel(**user_from_db)
    return user_model


# add user
async def add_user(
    user: UserModel,
) -> tuple[bool, UserModel]:
    try:
        # user.email is unique
        user_from_db = await db.users.find_one(
            {"email": user.email, "auth_provider": user.auth_provider}
        )
        if user_from_db is None:
            user.service_email = user.email
            await db.users.insert_one(user.model_dump())
        else:
            user = UserModel(**user_from_db)
            logging.debug("User already exists")
            return False, user
    except Exception as e:
        raise e
    return True, user


# patch user
async def patch_user_by_email(
    email: str,
    auth_provider: OAuthProvider,
    user_info: PatchableUserInfo,
) -> tuple[bool, UserInfo | None]:
    try:
        user_from_db = await db.users.find_one(
            {
                "email": email,
                "auth_provider": auth_provider,
            }
        )
        if user_from_db is None:
            return False, None
        updated_user_info = await db.users.find_one_and_update(
            {"email": email, "auth_provider": auth_provider},
            {"$set": user_info.model_dump(exclude_unset=True)},
            return_document=ReturnDocument.AFTER,
        )
        print(f"updated_user_info: {updated_user_info}")
        return True, UserInfo(**updated_user_info)
    except Exception as e:
        logging.exception("Error while patching user: %s", e)
        return False, None


async def get_user_by_ids(
    user_ids: list[str],
) -> tuple[bool, list[UserInfo]]:
    try:
        users_from_db = await db.users.find({"id": {"$in": user_ids}}).to_list(None)
        if users_from_db is None:
            return False, []
        return True, [UserInfo(**user) for user in users_from_db]
    except Exception as e:
        logging.exception("Error while getting users: %s", e)
        return False, []


async def patch_user_plan(
    email: str,
    auth_provider: OAuthProvider,
    plan: Plan,
    month: int,
) -> tuple[bool, UserInfo | None]:
    try:
        user_from_db = await db.users.find_one(
            {
                "email": email,
                "auth_provider": auth_provider,
            }
        )
        if user_from_db is None:
            return False, None

        plan_expired_at = datetime.now() + timedelta(days=30 * month)
        updated_user_info = await db.users.find_one_and_update(
            {"email": email, "auth_provider": auth_provider},
            {
                "$set": {
                    "using_plan": plan,
                    "plan_expired_at": plan_expired_at,
                }
            },
            return_document=ReturnDocument.AFTER,
        )
        return True, UserInfo(**updated_user_info)
    except Exception as e:
        logging.exception("Error while patching user: %s", e)
        return False, None


async def patch_user_profile_image(
    email: str,
    auth_provider: OAuthProvider,
    profile_image: str,
):
    try:
        user_from_db = await db.users.find_one(
            {
                "email": email,
                "auth_provider": auth_provider,
            }
        )
        if user_from_db is None:
            return False, None
        updated_user_info = await db.users.find_one_and_update(
            {"email": email, "auth_provider": auth_provider},
            {"$set": {"profile_image": profile_image}},
            return_document=ReturnDocument.AFTER,
        )
        return True, UserInfo(**updated_user_info)
    except Exception as e:
        logging.exception("Error while patching user: %s", e)
        return False, None


async def get_user_picture_meta(
    user_id: str,
) -> tuple[bool, dict | None]:
    try:
        meta_from_db = await db.picture_meta.find_one(
            {
                "user_id": user_id,
            }
        )
        if meta_from_db is None:
            return False, None
        return True, meta_from_db
    except Exception as e:
        logging.exception("Error while getting user picture meta: %s", e)
        return False, None


async def push_user_picture_id(
    user_id: str,
    picture_id: str,
) -> bool:
    try:
        await db.picture_meta.update_one(
            {"user_id": user_id},
            {
                "$push": {"ids": picture_id},
                "$setOnInsert": {"user_id": user_id},
                "$set": {"modified_at": datetime.now()},
            },
            upsert=True,
        )
    except Exception as e:
        logging.exception("Error while pushing user picture id: %s", e)
        return False
    return True


async def keep_user_on_track(
    from_user_id: str,
    to_user_id: str,
    distance: DistanceType,
) -> bool:
    try:
        # 만약 이미 로그가 존재한다면 업데이트
        await db.orbit_logs.find_one_and_update(
            {
                "from_user_id": from_user_id,
                "to_user_id": to_user_id,
            },
            {
                "$set": {
                    "distance": distance,
                    "updated_at": datetime.now(),
                }
            },
            upsert=True,
        )
    except Exception as e:
        logging.exception("Error while keeping user on track: %s", e)
        return False
    return True


async def kick_user_off_track(
    from_user_id: str,
    to_user_id: str,
) -> bool:
    try:
        await db.orbit_logs.delete_one(
            {
                "from_user_id": from_user_id,
                "to_user_id": to_user_id,
            }
        )
    except Exception as e:
        logging.exception("Error while kicking user off track: %s", e)
        return False
    return True


async def get_user_orbit_models(
    user_id: str,
) -> list[OrbitModel]:
    try:
        orbit_logs = await db.orbit_logs.find(
            {
                "from_user_id": user_id,
            }
        ).to_list(None)
    except Exception as e:
        logging.exception("Error while getting user orbit logs: %s", e)
        return []
    return [OrbitModel(**orbit_log) for orbit_log in orbit_logs]


async def add_foot_print(
    from_user_id: str,
    to_user_id: str,
    foot_print: FootPrintBody,
) -> bool:
    try:
        await db.orbit_logs.find_one_and_update(
            {
                "from_user_id": from_user_id,
                "to_user_id": to_user_id,
            },
            {
                # insert foot print
                "$push": {
                    "foot_prints": FootPrintModel(
                        **foot_print.model_dump()
                    ).model_dump(),
                },
            },
            upsert=True,
        )
    except Exception as e:
        logging.exception("Error while adding foot print: %s", e)
        return False
    return True


async def remove_foot_print(
    from_user_id: str,
    to_user_id: str,
    foot_print_id: str,
) -> bool:
    try:
        await db.orbit_logs.find_one_and_update(
            {
                "from_user_id": from_user_id,
                "to_user_id": to_user_id,
            },
            {
                # remove foot print
                "$pull": {
                    "foot_prints": {
                        "id": foot_print_id,
                    }
                },
            },
        )
    except Exception as e:
        logging.exception("Error while removing foot print: %s", e)
        return False
    return True


async def add_token_log(payload: TokenLog):
    try:
        await db.token_logs.insert_one(payload.model_dump())
    except Exception as e:
        raise e
    return True


async def ping():
    return await db.command("ping")
