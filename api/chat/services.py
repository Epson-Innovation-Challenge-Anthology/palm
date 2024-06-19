from api.chat.groq_cloud import GroqCloud
from api.settings import env
from schemas.chat import AskBody


async def ask_something(body: AskBody) -> str | None:
    """
    groq 프롬프트 실행
    """
    async with GroqCloud(api_key=env.groq_api_key) as groq_cloud:
        return await groq_cloud.ask(body.content)
