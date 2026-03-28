from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class LancamentoCriar(BaseModel):
    usuario_id: Optional[int] = Field(default=None, ge=1)
    categoria_id: int
    tipo: str
    valor: Decimal = Field(gt=0, decimal_places=2)
    descricao: Optional[str] = Field(default=None, max_length=255)
    periodicidade_ganho: Optional[str] = None
    minutos_corrida: Optional[int] = Field(default=None, ge=1)
    km_corrida: Optional[Decimal] = Field(default=None, gt=0, decimal_places=2)
    data_lancamento: Optional[date] = None
    moto_usuario_id: Optional[int] = None


class LancamentoResposta(BaseModel):
    id: int
    usuario_id: int
    categoria_id: int
    moto_usuario_id: Optional[int]
    tipo: str
    valor: Decimal
    descricao: Optional[str]
    periodicidade_ganho: Optional[str]
    minutos_corrida: Optional[int]
    km_corrida: Optional[Decimal]
    data_lancamento: date
    data_criacao: datetime

    class Config:
        from_attributes = True
