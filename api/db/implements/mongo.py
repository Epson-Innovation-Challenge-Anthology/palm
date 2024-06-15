import logging

from api.db.persistant import mongo as db
from enums.auth import OAuthProvider
from schemas.auth import TokenLog
from schemas.users import UserModel


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
            # logging.warning(f"User not found: {email}")
    except Exception as e:
        raise e
    return UserModel(**user_from_db)


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


async def add_token_log(payload: TokenLog):
    try:
        await db.token_logs.insert_one(payload.model_dump())
    except Exception as e:
        raise e
    return True


async def ping():
    return await db.command("ping")
