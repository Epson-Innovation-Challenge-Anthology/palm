from functools import lru_cache
from pathlib import Path
from typing import Any, Tuple, Type

from pydantic.fields import FieldInfo
from pydantic_settings import (
    BaseSettings,
    EnvSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

from api.enums import Environment, LogLevel

BASE_PATH = Path(__file__).parent.absolute()
DESCRIPTION = "DESCRIPTION.md"
INDEX_HTML = "index.html"


def kv_string_to_dict(comma_seperated_data: str) -> dict:
    """
    "key1:value1,key2:value2" -> {"key1": "value1", "key2": "value2"}
    """
    kv_map_list = [
        kv_string.split(":") for kv_string in comma_seperated_data.split(",")
    ]
    return {k: v for k, v in kv_map_list}


class MyCustomSource(EnvSettingsSource):
    def prepare_field_value(
        self, field_name: str, field: FieldInfo, value: Any, value_is_complex: bool
    ) -> Any:
        # Examples
        # if field_name == "allowed_services":
        #     return value.split(",")
        # if field_name in ("dust_service_map", "service_auth_map"):
        #     return kv_string_to_dict(value)
        return value


class Settings(BaseSettings):
    """
    Settings for the app.
    """

    service_name: str = "palm"
    environment: Environment = Environment.TEST
    loglevel: LogLevel = LogLevel.DEBUG
    enable_cors: bool = True
    cors_origins: str = ""
    mongo_host: str = ""
    mongo_port: int = 27017
    mongo_db: str = ""
    mongo_username: str | None = None
    mongo_password: str | None = None
    mongo_auth_source: str | None = None
    redis_host: str = ""
    redis_port: int = 6379
    redis_username: str | None = None
    redis_password: str | None = None
    redis_db: int = 0
    storage_access_key: str | None = None
    storage_secret_key: str | None = None
    storage_bucket_name: str = ""
    storage_endpoint: str = ""
    app_access_token_expire_minutes: int = 60
    app_refresh_token_expire_minutes: int = 60 * 24 * 30 * 6  # 6 months
    app_secret: str = ""
    app_secret_algo: str = "HS256"
    app_version: str = "0.0.1"
    frontend_url: str = ""
    google_client_id: str = ""
    google_client_secret: str = ""
    kakao_client_id: str = ""
    kakao_client_secret: str = ""

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (MyCustomSource(settings_cls),)

    model_config = SettingsConfigDict(
        env_prefix="palm_",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    """
    Returns the settings for the app.
    """
    env_ = Settings()
    return env_


@lru_cache
def get_description(base_path: Path = BASE_PATH) -> str:
    """Get description from README.md."""
    with open(base_path.parent / DESCRIPTION, "r", encoding="utf-8") as f:
        return f.read()


@lru_cache
def read_index_html():
    with open(
        BASE_PATH / INDEX_HTML,
        encoding="utf-8",
    ) as f:
        return f.read()


env = get_settings()

SERVICE_INFO = {
    "title": "PALM",
    "version": "0.0.1",
}
