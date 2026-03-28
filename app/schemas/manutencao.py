from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class ManutencaoCriar(BaseModel):
    usuario_id: Optional[int] = Field(default=None, ge=1)
    moto_usuario_id: Optional[int] = Field(default=None, ge=1)
    categoria_id: int

    valor_total: Decimal = Field(gt=0, decimal_places=2)

    km_atual: Optional[int] = Field(default=None, ge=0)
    data_manutencao: Optional[date] = None

    descricao: Optional[str] = Field(default=None, max_length=255)
    descricao_servico: Optional[str] = Field(default=None, max_length=255)
    oficina: Optional[str] = Field(default=None, max_length=120)
    tipo_servico: Optional[str] = Field(default=None, max_length=80)


class ManutencaoResposta(BaseModel):
    id: int
    usuario_id: int
    moto_usuario_id: Optional[int]
    lancamento_id: int

    valor_total: Decimal
    km_atual: Optional[int]

    data_manutencao: date
    data_criacao: datetime

    descricao_servico: Optional[str]
    oficina: Optional[str]
    tipo_servico: Optional[str]

    class Config:
        from_attributes = True
