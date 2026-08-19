from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UsuarioCriar(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    email: EmailStr
    senha: str = Field(min_length=6, max_length=72)

    @field_validator("email", mode="before")
    @classmethod
    def normalizar_email(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip().lower()
        return v


class UsuarioResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    email: EmailStr
    email_confirmado: bool = False
