from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Body, Depends, Path, status

from api.jwt import get_current_user_email_bearer
from api.messages import MESSAGES
from api.plan import services as plan_services
from responses.common import custom_response
from schemas import ResponseModel
from schemas.plan import Plan, PlanInfo, SubscriptionResult

router = APIRouter(prefix="/plan", tags=["plan"])


@router.post(
    "/subscribe/{plan}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": MESSAGES.PLAN_SUBSCRIBE_SUCCESS,
            "model": ResponseModel[SubscriptionResult].inject(
                message=MESSAGES.PLAN_SUBSCRIBE_SUCCESS,
                data=SubscriptionResult,
            ),
        },
    },
)
async def subscribe_plan(
    plan: Annotated[Plan, Path(description="구독할 요금제", example="BASIC")],
    payload: Annotated[PlanInfo, Body(description="구독 정보")],
    token_payload=Depends(get_current_user_email_bearer),
):
    """
    구독 활성화를 위해 호출해야하는 엔드포인트입니다.

    결제인증을 위한 트랜잭션 ID가 필요합니다.
    개발단계에서는 어떤 값을 넣어도 구독이 성공합니다.

    ---

    | plan | description |
    | ---- | ----------- |
    | 1    | BASIC       |
    | 2    | BEGINNER    |
    | 3    | EXPERT      |
    | 4    | MASTER      |
    """
    transaction_id = payload.transaction_id
    okay, status_code, user_info = await plan_services.activate_plan(
        payload=token_payload,
        month=payload.month,
        plan=plan,
        _transaction_id=transaction_id or "dummy",
    )
    """
    return:
        0: 실패 -> 예외
        1: 성공
        2: 실패 -> 사용자 정보 없음
        3: 실패 -> 트랜잭션 ID 불일치
        5: 실패 -> 이미 같은 플랜 구독 중
        6: 실패 -> 서버오류
    """

    if not okay:
        if status_code == 2:
            return custom_response(
                status_code=status.HTTP_404_NOT_FOUND,
                content=ResponseModel(
                    message=MESSAGES.USER_NOT_FOUND,
                    data=SubscriptionResult(
                        success=False,
                        plan=plan,
                        activated_at=None,
                        plan_expired_at=None,
                        month=None,
                    ),
                ),
            )
        elif status_code == 3:
            return custom_response(
                status_code=status.HTTP_403_FORBIDDEN,
                content=ResponseModel(
                    message=MESSAGES.PLAN_TRANSACTION_FAIL,
                    data=SubscriptionResult(
                        success=False,
                        plan=plan,
                        activated_at=None,
                        plan_expired_at=None,
                        month=None,
                    ),
                ),
            )
        elif status_code == 5:
            return custom_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=ResponseModel(
                    message=MESSAGES.ALREADY_SUBSCRIBED_PLAN,
                    data=SubscriptionResult(
                        success=False,
                        plan=plan,
                        activated_at=None,
                        plan_expired_at=None,
                        month=None,
                    ),
                ),
            )
        elif status_code == 6:
            return custom_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ResponseModel(
                    message=MESSAGES.PLAN_SUBSCRIBE_FAIL,
                    data=SubscriptionResult(
                        success=False,
                        plan=plan,
                        activated_at=None,
                        plan_expired_at=None,
                        month=None,
                    ),
                ),
            )
        else:
            return custom_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ResponseModel(
                    message=MESSAGES.PLAN_SUBSCRIBE_FAIL,
                    data=SubscriptionResult(
                        success=False,
                        plan=plan,
                        activated_at=None,
                        plan_expired_at=None,
                        month=None,
                    ),
                ),
            )
    month = payload.month
    return custom_response(
        status_code=status.HTTP_200_OK,
        content=ResponseModel(
            message=MESSAGES.PLAN_SUBSCRIBE_SUCCESS,
            data=SubscriptionResult(
                success=True,
                plan=plan,
                activated_at=user_info.plan_expired_at - timedelta(days=30 * month),  # type: ignore
                plan_expired_at=user_info.plan_expired_at,  # type: ignore
                month=month,
            ),
        ),
    )


@router.delete(
    "/subscribe",
    status_code=status.HTTP_200_OK,
)
async def do_unsubscribe(
    token_payload=Depends(get_current_user_email_bearer),
):
    okay = await plan_services.unsubscribe_plan(payload=token_payload)
    if not okay:
        return custom_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ResponseModel(
                message=MESSAGES.UNSUBSCRIBE_FAIL,
                data=None,
            ),
        )
    return custom_response(
        status_code=status.HTTP_200_OK,
        content=ResponseModel(
            message=MESSAGES.UNSUBSCRIBE_SUCCESS,
            data=None,
        ),
    )
