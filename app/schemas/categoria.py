from pydantic import BaseModel, Field


class CategoriaResposta(BaseModel):
    id: int
    usuario_id: int | None
    nome: str
    tipo: str
    grupo_despesa: str | None
    ativo: bool

    class Config:
        from_attributes = True


class CategoriaCriar(BaseModel):
    nome: str = Field(min_length=2, max_length=100)
    tipo: str
    grupo_despesa: str | None = None
