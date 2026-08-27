from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class MetaCriar(BaseModel):
    nome: str = Field(min_length=2, max_length=80)
    tipo: str
    periodo: str
    valor_meta: Decimal = Field(gt=0, decimal_places=2)
    dias_trabalho_semana: Optional[int] = Field(default=6, ge=1, le=7)
    categoria_cofre: Optional[str] = None
    ativa: bool = True


class MetaAtualizar(BaseModel):
    nome: Optional[str] = Field(default=None, min_length=2, max_length=80)
    tipo: Optional[str] = None
    periodo: Optional[str] = None
    valor_meta: Optional[Decimal] = Field(default=None, gt=0, decimal_places=2)
    dias_trabalho_semana: Optional[int] = Field(default=None, ge=1, le=7)
    categoria_cofre: Optional[str] = None
    ativa: Optional[bool] = None


class MetaResposta(BaseModel):
    id: int
    usuario_id: int
    nome: str
    tipo: str
    periodo: str
    valor_meta: Decimal
    dias_trabalho_semana: Optional[int] = 6
    categoria_cofre: Optional[str] = None
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
    dias_trabalho_semana: Optional[int] = 6
    categoria_cofre: Optional[str] = None
    periodo_inicio: date
    periodo_fim: date
    realizado: Decimal
    valor_restante: Decimal
    meta_diaria_necessaria: Optional[Decimal] = Decimal("0")
    dias_trabalho_restantes: Optional[int] = 0
    progresso_periodo_percentual: Decimal
    percentual_meta: Decimal
    status: str
    recomendacao: str
