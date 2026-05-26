from pydantic_settings import BaseSettings, SettingsConfigDict

from common.enums import DatabaseOption, StageOption


class Settings(BaseSettings):
    API_VERSION: str = "1.0"
    API_URL_PREFIX: str = "/api"
    ROOT_PATH: str = ""
    STAGE: StageOption = StageOption.LOCAL
    DEBUG: bool = True

    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore", env_file_encoding="utf-8"
    )


class AwsSettings(BaseSettings):
    DEPLOY_REGION: str = ""
    COGNITO_USER_POOL_ID: str = ""
    COGNITO_CLIENT_ID: str = ""
    COGNITO_CLIENT_SECRET: str = ""
    COGNITO_USER_POOL_DOMAIN: str = ""
    BACKEND_BUCKET_NAME: str = ""
    WS_LAMBDA_ARN: str = ""
    WS_ENDPOINT: str = ""
    ECS_REPORTS_API_URL: str = ""
    COLLECTION_LOAD_DATA: str = ""
    COLLECTION_PROGRESS_DATA: str = ""
    CLOUDFRONT_PUBLIC_KEY: str = ""
    SECRET_CLOUDFRONT_PRIVATE_KEY: str = ""
    CLOUDFRONT_DISTRIBUTION: str = ""
    REDIS_ENDPOINT: str = ""
    REDIS_PORT: str = ""
    QUEUE_AUDIT_EVENT_URL: str = ""
    QUEUE_CORE_TO_RECOGNITION_URL: str = ""

    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore", env_file_encoding="utf-8"
    )


class DatabaseSettings(BaseSettings):
    DATABASE: DatabaseOption = DatabaseOption.POSTGRES
    POSTGRES_HOST: str = "localhost"
    POSTGRES_HOSTS_READ_REPLICA: str = ""
    POSTGRES_PORT: str = "5432"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_NAME: str = "postgres"

    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore", env_file_encoding="utf-8"
    )


settings = Settings()
aws_settings = AwsSettings()
database_settings = DatabaseSettings()

settings.ROOT_PATH = f"/{settings.STAGE.value}-tf" if settings.STAGE else ""
