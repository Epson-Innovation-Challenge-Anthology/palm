from fastapi import APIRouter, BackgroundTasks, Body, status

from api.messages import MESSAGES
from api.misc import services as misc_services
from responses.common import custom_response
from schemas import ResponseModel
from schemas.misc import MailContent

router = APIRouter(prefix="/misc", tags=["misc"])


@router.post(
    "/send-mail",
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        status.HTTP_202_ACCEPTED: {
            "description": MESSAGES.MAIL_SENT,
        },
    },
)
async def send_mail(
    background_tasks: BackgroundTasks,
    content: MailContent = Body(...),
):
    """
    고객문의, 이메일 발송
    """
    background_tasks.add_task(misc_services.send_mail, content)
    return custom_response(
        status_code=status.HTTP_202_ACCEPTED,
        content=ResponseModel(message=MESSAGES.MAIL_SENT, data=None),
    )
