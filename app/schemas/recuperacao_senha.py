from pydantic import BaseModel, EmailStr, Field, field_validator


class SolicitarRecuperacao(BaseModel):
    email: EmailStr

    @field_validator("email", mode="before")
    @classmethod
    def normalizar_email(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip().lower()
        return v


class RedefinirSenha(BaseModel):
    email: EmailStr
    codigo_pin: str = Field(min_length=6, max_length=6)
    nova_senha: str = Field(min_length=6, max_length=72)

    @field_validator("email", mode="before")
    @classmethod
    def normalizar_email(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip().lower()
        return v


class AlterarSenhaLogado(BaseModel):
    senha_atual: str = Field(min_length=6, max_length=72)
    nova_senha: str = Field(min_length=6, max_length=72)
