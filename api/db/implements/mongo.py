import logging
from datetime import datetime, timedelta

from pymongo import ReturnDocument

from api.db.persistant import mongo as db
from enums.auth import OAuthProvider
from enums.users import Plan
from schemas.auth import TokenLog
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


async def add_token_log(payload: TokenLog):
    try:
        await db.token_logs.insert_one(payload.model_dump())
    except Exception as e:
        raise e
    return True


async def ping():
    return await db.command("ping")
