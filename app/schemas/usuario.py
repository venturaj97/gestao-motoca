from pydantic import BaseModel, EmailStr, Field


class UsuarioCriar(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    email: EmailStr
    senha: str = Field(min_length=6, max_length=72)


class UsuarioResposta(BaseModel):
    id: int
    nome: str
    email: EmailStr

    class Config:
        from_attributes = True
