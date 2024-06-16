from api.db.implements.mongo import get_user_by_email, patch_user_plan
from api.jwt import TokenPayload
from enums.users import PLAN_MAP, Plan
from schemas.users import UserInfo


async def activate_plan(
    payload: TokenPayload,
    plan: Plan,
    month: int,
    _transaction_id: str,
) -> tuple[bool, int, UserInfo | None]:
    """
    인증정보 확인 후 구독 활성화

    return:
        1: 성공
        2: 실패 -> 사용자 정보 없음
        3: 실패 -> 트랜잭션 ID 불일치
        # 4: 실패 -> 상위 티어 구독 중
        5: 실패 -> 이미 구독 중
        6: 실패 -> 서버오류
    """
    # TODO: check transaction_id from redis
    # return False, 3

    user_info = await get_user_by_email(
        email=payload.email,
        auth_provider=payload.auth_provider,
    )
    if not user_info:
        return False, 2, None

    using_plan = user_info.using_plan
    # if PLAN_MAP[using_plan] > PLAN_MAP[plan]:
    #     return False, 4, None
    if PLAN_MAP[using_plan] == PLAN_MAP[plan]:
        return False, 5, None
    else:
        okay, user_info = await patch_user_plan(
            email=payload.email,
            auth_provider=payload.auth_provider,
            plan=plan,
            month=month,
        )
        if not okay:
            return False, 6, None
    return True, 1, user_info


async def unsubscribe_plan(
    payload: TokenPayload,
) -> bool:
    """
    구독 해지
    """
    user_info = await get_user_by_email(
        email=payload.email,
        auth_provider=payload.auth_provider,
    )
    if not user_info:
        return False
    okay, user_info = await patch_user_plan(
        email=payload.email,
        auth_provider=payload.auth_provider,
        plan=Plan.BASIC,
        month=0,
    )
    if not okay:
        return False
    return True
