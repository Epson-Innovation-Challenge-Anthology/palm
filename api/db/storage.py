import asyncio
import logging
import os
import zipfile

from boto3 import client as boto3_client
from boto3.session import Session
from botocore.response import StreamingBody

logging.basicConfig(level=logging.INFO)


class BucketManager:
    """
    S3 버킷에 파일을 업로드하거나 다운로드 할 수 있습니다.
    """

    client: boto3_client
    bucket: Session
    access_key: str
    secret_key: str
    bucket_name: str
    endpoint_url: str

    def __init__(
        self,
        access_key: str,
        secret_key: str,
        bucket_name: str,
        endpoint_url: str = "",
        base_path: str = "food-recognition",
    ):
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket_name = bucket_name
        self.endpoint_url = endpoint_url
        self.base_path = base_path
        self.client = None

    async def __aenter__(self):
        logging.debug("s3 client opened")
        self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        self.client = None
        logging.debug("s3 client closed")

    def __enter__(self):
        logging.debug("s3 client opened")
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.client = None
        logging.debug("s3 client closed")

    def file_url(self, key):
        file_url_ = f"{self.endpoint_url}/{self.bucket_name}/{key}"
        logging.debug("file_url: %s", file_url_)
        return file_url_

    def initialize(self):
        self.client = boto3_client(
            service_name="s3",  # service name
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            endpoint_url=self.endpoint_url,
        )
        logging.debug("s3 client initialized")

    async def download_file(self, filename: str):
        """
        파일을 다운로드합니다.
        """
        key = f"{self.base_path}/{filename}"
        logging.info("download_file: <filename: %s> <key: %s>", filename, key)
        self.client.download_file(
            self.bucket_name,
            key,
            filename,
        )

    async def download_data(self, filename: str) -> bytes:
        """
        스토리지에 있던 파일을 메모리에 다운로드합니다.
        """
        key = f"{self.base_path}/{filename}"
        logging.debug("download_fileobj: <filename: %s> <key: %s>", filename, key)
        try:
            obj = self.client.get_object(
                Bucket=self.bucket_name,
                Key=key,
            )
        except Exception as e:
            raise KeyError("Key not found") from e
        if not obj.get("Body"):
            raise KeyError("s3 client get_object response has no 'Body' key")
        if not isinstance(obj["Body"], StreamingBody):
            raise TypeError(
                "s3 client get_object response 'Body' is not StreamingBody"
                f" but {type(obj['Body'])}"
            )
        bytes_ = obj["Body"].read()
        return bytes_


def _unzip(zip_file: str):
    """
    압축 파일을 풉니다.
    """
    logging.debug("unzip: <zip_file: %s>", zip_file)
    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        zip_ref.extractall()
    logging.debug("unzip: done")


async def unzip(zip_file: str):
    """
    압축 파일을 풉니다.
    """
    await asyncio.to_thread(_unzip, zip_file)


def file_exists(file_path: str) -> bool:
    """
    파일이 존재하는지 확인합니다.
    """
    logging.debug("file_exists: <file_path: %s>", file_path)
    return os.path.exists(file_path)


def touch_file(file_path: str):
    """
    파일을 생성합니다.
    """
    logging.debug("touch_file: <file_path: %s>", file_path)
    with open(file_path, "w", encoding="utf-8") as _:
        pass


def remove_file(file_path: str):
    """
    파일을 삭제합니다.
    """
    logging.debug("remove_file: <file_path: %s>", file_path)
    try:
        os.remove(file_path)
    except FileNotFoundError:
        pass


async def test():
    logging.info("storage.py")
    bucket = BucketManager(
        access_key="default",
        secret_key="qwer1234",
        bucket_name="local",
        endpoint_url="http://localhost:25053",
        base_path="food-recognition",
    )
    bucket.initialize()
    await bucket.download_file("models.zip")


if __name__ == "__main__":
    asyncio.run(test())
