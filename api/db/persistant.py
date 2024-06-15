import asyncio
import logging

from motor.motor_asyncio import AsyncIOMotorClient

from api.enums import Environment
from api.settings import env

# pylint: disable=C0301


def get_mongo_client() -> AsyncIOMotorClient:
    """
    MongoDB 클라이언트를 반환합니다.
    """
    logging.info("Environment -> %s", env.environment)
    if env.environment in [Environment.DEVELOPMENT, Environment.PRODUCTION]:
        # NOTE: MongoDB Atlas에 연결하기위한 정보
        # 사용하는 환경에 알맞게 수정해주세요.
        MONGO_URL = f"mongodb+srv://{env.mongo_username}:{env.mongo_password}@{env.mongo_host}/?retryWrites=true&w=majority"
        logging.info("MONGO URL -> %s", MONGO_URL)
        return AsyncIOMotorClient(MONGO_URL)
    else:
        MONGO_URL = (
            f"mongodb://{env.mongo_host}:{env.mongo_port}/?retryWrites=true&w=majority"
        )
        if not env.mongo_username:
            return AsyncIOMotorClient(MONGO_URL)
        else:
            return AsyncIOMotorClient(
                MONGO_URL,
                username=env.mongo_username,
                password=env.mongo_password,
            )


g_client = get_mongo_client()
g_client.get_io_loop = asyncio.get_running_loop

mongo = g_client[env.mongo_db]
