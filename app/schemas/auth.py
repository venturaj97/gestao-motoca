from pydantic import BaseModel, EmailStr, Field


class LoginEntrada(BaseModel):
    email: EmailStr
    senha: str = Field(min_length=6, max_length=72)


class TokenResposta(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshEntrada(BaseModel):
    refresh_token: str


class UsuarioLogadoResposta(BaseModel):
    id: int
    nome: str
    email: EmailStr
