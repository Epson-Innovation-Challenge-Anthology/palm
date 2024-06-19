import logging

from groq import Groq


class GroqCloud:
    def __init__(self, api_key: str):
        self.client = Groq(
            api_key=api_key,
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def ask(self, content: str) -> str | None:
        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": content,
                }
            ],
            model="llama3-8b-8192",
        )
        logging.info("chat_completion: %s", chat_completion)
        return chat_completion.choices[0].message.content
