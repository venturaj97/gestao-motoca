from pydantic import BaseModel, Field
from typing import Optional


class MotoUsuarioCriar(BaseModel):
    usuario_id: int

    moto_versao_id: Optional[int] = None

    marca_manual: Optional[str] = None
    modelo_manual: Optional[str] = None
    ano_manual: Optional[int] = None

    km_atual: int = Field(ge=0)
    cor: Optional[str] = None


class MotoUsuarioResposta(BaseModel):
    id: int
    usuario_id: int
    moto_versao_id: Optional[int]
    marca_manual: Optional[str]
    modelo_manual: Optional[str]
    ano_manual: Optional[int]
    km_atual: int
    cor: Optional[str]
    ativa: bool = True

    class Config:
        from_attributes = True


class MotoUsuarioAtivaAlterar(BaseModel):
    usuario_id: int = Field(ge=1)
    moto_usuario_id: int = Field(ge=1)
    ativa: bool