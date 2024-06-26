import logging

from api.db.implements import mongo
from enums.orbit import DistanceType
from schemas.orbit import FootPrintBody, OrbitInfo


async def keep_user_on_track(
    from_user_id: str,
    to_user_id: str,
    distance: DistanceType,
) -> bool:
    try:
        await mongo.keep_user_on_track(
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            distance=distance,
        )
        logging.info("User %s is on %s track", to_user_id, from_user_id)
    except Exception as e:
        logging.exception("Error while keeping user on track: %s", e)
        return False
    return True


async def kick_user_off_track(
    from_user_id: str,
    to_user_id: str,
) -> bool:
    try:
        await mongo.kick_user_off_track(
            from_user_id=from_user_id,
            to_user_id=to_user_id,
        )
        logging.info("User %s is off track", to_user_id)
    except Exception as e:
        logging.exception("Error while kicking user off track: %s", e)
        return False
    return True


async def get_user_orbit_info(
    user_id: str,
) -> list[OrbitInfo]:
    try:
        orbit_models = await mongo.get_user_orbit_models(
            user_id=user_id,
        )
    except Exception as e:
        logging.exception("Error while getting user orbit logs: %s", e)
        return []
    orbit_user_ids = [model.to_user_id for model in orbit_models]
    _, orbit_users = await mongo.get_user_by_ids(orbit_user_ids)
    orbit_info = [
        OrbitInfo(
            distance=model.distance,
            user_id=model.to_user_id,
            friend_name=orbit_users[i].name or "김앤솔",
            foot_prints=model.foot_prints,
        )
        for i, model in enumerate(orbit_models)
    ]
    return orbit_info


async def add_foot_print(
    from_user_id: str,
    to_user_id: str,
    foot_print: FootPrintBody,
) -> bool:
    try:
        await mongo.add_foot_print(
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            foot_print=foot_print,
        )
        logging.info("User %s added foot print to %s", from_user_id, to_user_id)
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
        await mongo.remove_foot_print(
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            foot_print_id=foot_print_id,
        )
        logging.info("User %s removed foot print from %s", from_user_id, to_user_id)
    except Exception as e:
        logging.exception("Error while removing foot print: %s", e)
        return False
    return True
