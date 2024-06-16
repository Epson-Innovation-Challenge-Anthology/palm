from datetime import datetime, timedelta

from pydantic import BaseModel, Field

from enums.users import Plan


class PlanFields:
    plan = Field(
        ...,
        description="사용자의 구독 플랜",
        json_schema_extra={"example": Plan.EXPERT},
    )
    transaction_id = Field(None, description="구독 인증에 필요한 트랜잭션 ID")
    success = Field(
        ..., description="구독 성공 여부", json_schema_extra={"example": True}
    )
    activated_at = Field(
        ...,
        description="구독 활성화 일시",
        json_schema_extra={"example": "2024-08-17 19:00:00.000000"},
        default_factory=datetime.now,
    )
    plan_expired_at = Field(
        ...,
        description="구독 만료 일시",
        json_schema_extra={"example": "2024-09-17 19:00:00.000000"},
        default_factory=lambda: datetime.now() + timedelta(days=30),
    )
    month: int = Field(1, description="구독 기간(월)", ge=1, le=12)


class PlanInfo(BaseModel):
    transaction_id: str | None = PlanFields.transaction_id
    month: int = PlanFields.month


class SubscriptionResult(BaseModel):
    success: bool = PlanFields.success
    plan: Plan | None = PlanFields.plan
    activated_at: datetime | None = PlanFields.activated_at
    plan_expired_at: datetime | None = PlanFields.plan_expired_at
    month: int | None = PlanFields.month
