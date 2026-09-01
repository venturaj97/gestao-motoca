from pydantic import Field
# pyrefly: ignore [missing-import]
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
    auth_refresh_token_exp_dias: int = Field(default=30, validation_alias="AUTH_REFRESH_TOKEN_EXP_DIAS")
    cors_origins: list[str] = Field(
        default=[
            "http://localhost:5173",
            "http://localhost:5174",
            "http://localhost:5175",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:5174",
            "http://127.0.0.1:5175",
            "http://localhost:4173",
            "http://192.168.1.69:5173",
        ],
        validation_alias="CORS_ORIGINS",
    )

    smtp_host: str = Field(default="smtp.gmail.com", validation_alias="SMTP_HOST")
    smtp_port: int = Field(default=587, validation_alias="SMTP_PORT")
    smtp_user: str = Field(default="", validation_alias="SMTP_USER")
    smtp_password: str = Field(default="", validation_alias="SMTP_PASSWORD")
    smtp_from: str = Field(default="", validation_alias="SMTP_FROM")
    smtp_tls: bool = Field(default=True, validation_alias="SMTP_TLS")

    # ── Stripe ──
    stripe_secret_key: str = Field(default="", validation_alias="STRIPE_SECRET_KEY")
    stripe_publishable_key: str = Field(default="", validation_alias="STRIPE_PUBLISHABLE_KEY")
    stripe_webhook_secret: str = Field(default="", validation_alias="STRIPE_WEBHOOK_SECRET")
    stripe_price_mensal: str = Field(default="", validation_alias="STRIPE_PRICE_MENSAL")
    stripe_price_anual: str = Field(default="", validation_alias="STRIPE_PRICE_ANUAL")
    frontend_url: str = Field(default="http://localhost:5173", validation_alias="FRONTEND_URL")

    @property
    def database_url(self) -> str:
        from urllib.parse import quote_plus

        user = quote_plus(self.db_user)
        password = quote_plus(self.db_password)
        return (
            f"postgresql+psycopg://{user}:{password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


settings = Settings()

