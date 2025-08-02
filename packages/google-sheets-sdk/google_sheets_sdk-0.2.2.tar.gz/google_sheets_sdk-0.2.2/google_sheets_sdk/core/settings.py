from pydantic.networks import EmailStr, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="GOOGLE_SHEETS_",
        frozen=True,
    )

    PRIVATE_KEY_ID: str
    PRIVATE_KEY: str
    CLIENT_EMAIL: EmailStr
    SCOPE: HttpUrl
