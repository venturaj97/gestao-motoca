from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class AbastecimentoCriar(BaseModel):
    usuario_id: Optional[int] = Field(default=None, ge=1)
    moto_usuario_id: Optional[int] = Field(default=None, ge=1)
    categoria_id: int

    valor_total: Decimal = Field(gt=0, decimal_places=2)
    litros: Decimal = Field(gt=0, decimal_places=2)

    km_atual: Optional[int] = Field(default=None, ge=0)
    data_abastecimento: Optional[date] = None

    descricao: Optional[str] = Field(default=None, max_length=255)
    posto: Optional[str] = Field(default=None, max_length=120)
    tipo_combustivel: Optional[str] = Field(default=None, max_length=40)


class AbastecimentoResposta(BaseModel):
    id: int
    usuario_id: int
    moto_usuario_id: Optional[int]
    lancamento_id: int

    litros: Decimal
    valor_total: Decimal
    valor_litro: Decimal

    km_atual: Optional[int]
    data_abastecimento: date
    data_criacao: datetime

    posto: Optional[str]
    tipo_combustivel: Optional[str]

    class Config:
        from_attributes = True
