from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ambiente: str = "dev"

    db_host: str = Field(validation_alias="DB_HOST")
    db_port: int = Field(validation_alias="DB_PORT")
    db_name: str = Field(validation_alias="DB_NAME")
    db_user: str = Field(validation_alias="DB_USER")
    db_password: str = Field(validation_alias="DB_PASSWORD")
    wdapi_base_url: str = Field(
        default="https://wdapi2.com.br/consulta",
        validation_alias="WDAPI_BASE_URL",
    )
    wdapi_token: str = Field(default="", validation_alias="WDAPI_TOKEN")
    wdapi_timeout_segundos: int = Field(default=10, validation_alias="WDAPI_TIMEOUT_SEGUNDOS")
    auth_secret_key: str = Field(
        default="troque-esta-chave-em-producao",
        validation_alias="AUTH_SECRET_KEY",
    )
    auth_algorithm: str = Field(default="HS256", validation_alias="AUTH_ALGORITHM")
    auth_token_exp_minutos: int = Field(default=1440, validation_alias="AUTH_TOKEN_EXP_MINUTOS")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

settings = Settings()
