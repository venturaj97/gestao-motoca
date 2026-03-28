from pydantic import BaseModel, Field
from typing import Any, Optional


class MotoUsuarioCriar(BaseModel):
    usuario_id: Optional[int] = Field(default=None, ge=1)

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
    placa: Optional[str]
    origem_dados: str
    km_atual: int
    cor: Optional[str]
    ativa: bool = True

    class Config:
        from_attributes = True


class MotoUsuarioAtivaAlterar(BaseModel):
    moto_usuario_id: int = Field(ge=1)
    ativa: bool


class MotoUsuarioAtualizar(BaseModel):
    """Campos opcionais; envie apenas o que deseja alterar."""
    km_atual: Optional[int] = Field(default=None, ge=0)
    cor: Optional[str] = Field(default=None, max_length=40)
    ativa: Optional[bool] = None

    marca_manual: Optional[str] = Field(default=None, max_length=80)
    modelo_manual: Optional[str] = Field(default=None, max_length=120)
    ano_manual: Optional[int] = None


class ConsultaPlacaResposta(BaseModel):
    placa_consultada: str
    extra_disponivel: bool
    fipe_disponivel: bool
    fipe_melhor_correspondencia: Optional[dict[str, Any]] = None
    dados: dict[str, Any]


class MotoUsuarioCriarPorPlaca(BaseModel):
    placa: str = Field(min_length=7, max_length=8)
    km_atual: int = Field(default=0, ge=0)
    cor: Optional[str] = Field(default=None, max_length=40)
