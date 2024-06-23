import asyncio
import base64
import logging
import os
from datetime import datetime
from http import HTTPStatus

import aiohttp

HOST = "api.epsonconnect.com"
ACCEPT = "application/json;charset=utf-8"

# CLIENT_ID = env.epson_client_id
# SECRET = env.epson_client_secret
# DEVICE = env.epson_email_id


class Epson:
    auth: str = ""
    session: aiohttp.ClientSession

    def __init__(
        self, client_id: str, secret: str, device_id: str, handle_id: str
    ) -> None:
        self.auth = ""
        self.host = "api.epsonconnect.com"
        self.accept = "application/json;charset=utf-8"
        self.client_id = client_id
        self.secret = secret
        self.device_id = device_id
        self.access_token = ""
        self.subject_id = ""
        self.handle_id = handle_id or "palm"

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

    async def initialize(self):
        self.auth = base64.b64encode(
            (f"{self.client_id}:{self.secret}").encode()
        ).decode()
        await self.init_session()

    async def init_session(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5))

    async def _authorize(self, session) -> tuple[str, str]:
        AUTH_URI = (
            f"https://{self.host}/api/1/printing/oauth2/auth/token?subject=printer"
        )
        query_param = {
            "grant_type": "password",
            "username": self.device_id,
            "password": "",
        }
        headers = {
            "Authorization": "Basic " + self.auth,
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        }
        async with session.post(
            url=AUTH_URI,
            data=query_param,
            headers=headers,
        ) as res:
            body = await res.json()
            if res.status != HTTPStatus.OK:
                return "", ""
        access_token = body.get("access_token")
        subject_id = body.get("subject_id")
        self.access_token = access_token
        self.subject_id = subject_id
        return access_token, subject_id

    async def _create_job(
        self, session, access_token: str, subject_id: str
    ) -> tuple[str, str]:
        # 2. Create print job
        job_uri = f"https://{self.host}/api/1/printing/printers/{subject_id}/jobs"
        data_param = {"job_name": "SampleJob1", "print_mode": "document"}
        headers = {
            "Authorization": "Bearer " + access_token,
            "Content-Type": "application/json;charset=utf-8",
        }

        async with session.post(job_uri, json=data_param, headers=headers) as res:
            body = await res.json()
            logging.debug(job_uri)
            logging.debug(data_param)
            if res.status != HTTPStatus.CREATED:
                logging.debug("%s: %s", res.status, res.reason)
                logging.debug(body)
                return "", ""
            logging.debug("%s: %s", res.status, res.reason)
            logging.debug(body)

        job_id = body.get("id")
        base_uri = body.get("upload_uri")
        return job_id, base_uri

    async def _upload_file(self, session, job_id: str, base_uri: str, file_path: str):
        local_file_path = file_path
        _, ext = os.path.splitext(local_file_path)
        file_name = "1" + ext
        upload_uri = f"{base_uri}&File={file_name}"

        headers = {
            "Content-Length": str(os.path.getsize(local_file_path)),
            "Content-Type": "application/octet-stream",
        }

        async with session.post(
            upload_uri,
            data=open(local_file_path, "rb"),
            headers=headers,
        ) as res:
            body = await res.read()
            logging.debug(base_uri)
            if res.status != HTTPStatus.OK:
                logging.debug("%s: %s: %s", job_id, res.status, res.reason)
                logging.debug(body.decode())
                return False
            logging.debug("%s: %s: %s", job_id, res.status, res.reason)
        return True

    async def _execute_print(self, session, subject_id, job_id, access_token):
        # 4. Execute print
        print_uri = (
            f"https://{HOST}/api/1/printing/printers/{subject_id}/jobs/{job_id}/print"
        )
        headers = {
            "Authorization": "Bearer " + access_token,
            "Content-Type": "application/json; charset=utf-8",
        }

        async with session.post(print_uri, headers=headers) as res:
            body = await res.json()
            logging.debug("print_uri: %s", print_uri)
            if res.status != HTTPStatus.OK:
                logging.debug("%s: %s", res.status, res.reason)
                logging.debug(body)
                return False
            logging.debug("%s: %s", res.status, res.reason)
            logging.debug(body)
        return True

    async def print_file_by_path(self, file_path: str):
        async with aiohttp.ClientSession() as session:
            access_token, subject_id = await self._authorize(session)
            if not access_token or not subject_id:
                logging.exception("Failed to authorize")
                return False
            job_id, base_uri = await self._create_job(session, access_token, subject_id)
            if not job_id or not base_uri:
                logging.exception("Failed to create job")
                return False
            if not await self._upload_file(session, job_id, base_uri, file_path):
                logging.exception("Failed to upload_file")
                return False
            if not await self._execute_print(session, subject_id, job_id, access_token):
                logging.exception("Failed to execute print")
                return False
            logging.info("Success to print")
            return True


async def test():
    """
    TEST FUNCTION

    You need to set the following environment variables:
    PALM_EPSON_CLIENT_ID
    PALM_EPSON_CLIENT_SECRET
    PALM_EPSON_EMAIL_ID
    """
    client_id = os.getenv("PALM_EPSON_CLIENT_ID", "")
    secret = os.getenv("PALM_EPSON_CLIENT_SECRET", "")
    device_id = os.getenv("PALM_EPSON_EMAIL_ID", "")
    handle_id = datetime.now().strftime("%Y%m%d%H%M%S")
    async with Epson(client_id, secret, device_id, handle_id) as epson:
        await epson.print_file_by_path("test.pdf")


if __name__ == "__main__":
    asyncio.run(test())
