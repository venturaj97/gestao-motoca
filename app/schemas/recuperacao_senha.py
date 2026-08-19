from pydantic import BaseModel, EmailStr, Field


class SolicitarRecuperacao(BaseModel):
    email: EmailStr


class RedefinirSenha(BaseModel):
    email: EmailStr
    codigo_pin: str = Field(min_length=6, max_length=6)
    nova_senha: str = Field(min_length=6, max_length=72)


class AlterarSenhaLogado(BaseModel):
    senha_atual: str = Field(min_length=6, max_length=72)
    nova_senha: str = Field(min_length=6, max_length=72)
