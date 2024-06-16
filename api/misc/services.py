import asyncio
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from api.settings import env
from schemas.misc import MailContent


def _send_email(body: MailContent) -> None:
    # 이메일 발신자, 수신자, 앱 비밀번호 설정
    sender_email = receiver_email = "2024.co2palm.letsgo@gmail.com"
    password = env.google_mail_app_password

    # MIME 메시지 생성
    message = MIMEMultipart("alternative")
    message["Subject"] = (
        f"[고객문의] {body.family_name} {body.given_name}: {body.author_email}"
    )
    message["From"] = sender_email
    message["To"] = receiver_email

    # 이메일 본문: 텍스트와 HTML 버전
    text = body.content
    html = f"""\
    <html>
    <body>
        <pre>{body.content}</pre>
    </body>
    </html>
    """

    # MIMEText 객체 생성 및 메시지에 추가
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    message.attach(part1)
    message.attach(part2)

    # Gmail SMTP 서버를 통해 이메일 보내기
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())


async def send_mail(body: MailContent) -> None:
    """
    메일 발송기능 비동기 래핑 함수
    """
    _ = await asyncio.to_thread(_send_email, body)
    logging.debug("메일 발송 요청이 완료되었습니다.")
