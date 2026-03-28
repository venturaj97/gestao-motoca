from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class MetaCriar(BaseModel):
    nome: str = Field(min_length=2, max_length=80)
    tipo: str
    periodo: str
    valor_meta: Decimal = Field(gt=0, decimal_places=2)
    ativa: bool = True


class MetaAtualizar(BaseModel):
    nome: Optional[str] = Field(default=None, min_length=2, max_length=80)
    tipo: Optional[str] = None
    periodo: Optional[str] = None
    valor_meta: Optional[Decimal] = Field(default=None, gt=0, decimal_places=2)
    ativa: Optional[bool] = None


class MetaResposta(BaseModel):
    id: int
    usuario_id: int
    nome: str
    tipo: str
    periodo: str
    valor_meta: Decimal
    ativa: bool
    data_criacao: datetime

    class Config:
        from_attributes = True


class MetaAlertaResposta(BaseModel):
    meta_id: int
    nome: str
    tipo: str
    periodo: str
    valor_meta: Decimal
    periodo_inicio: date
    periodo_fim: date
    realizado: Decimal
    progresso_periodo_percentual: Decimal
    percentual_meta: Decimal
    status: str
    recomendacao: str
