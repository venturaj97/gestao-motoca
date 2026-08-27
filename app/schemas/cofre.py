from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class CofreCriar(BaseModel):
    nome: str = Field(min_length=2, max_length=80)
    categoria: str = Field(min_length=2, max_length=50)  # PNEU, SEGURO, IPVA, REVISAO, RESERVA, OUTROS
    valor_meta: Decimal = Field(gt=0, decimal_places=2)
    saldo_atual: Optional[Decimal] = Field(default=Decimal("0.00"), ge=0, decimal_places=2)
    porcentagem_autoguarda: Optional[Decimal] = Field(default=Decimal("0.00"), ge=0, le=100, decimal_places=2)
    ativa: bool = True


class CofreAtualizar(BaseModel):
    nome: Optional[str] = Field(default=None, min_length=2, max_length=80)
    categoria: Optional[str] = Field(default=None, min_length=2, max_length=50)
    valor_meta: Optional[Decimal] = Field(default=None, gt=0, decimal_places=2)
    saldo_atual: Optional[Decimal] = Field(default=None, ge=0, decimal_places=2)
    porcentagem_autoguarda: Optional[Decimal] = Field(default=None, ge=0, le=100, decimal_places=2)
    ativa: Optional[bool] = None


class CofreAporte(BaseModel):
    valor: Decimal = Field(gt=0, decimal_places=2)
    tipo_operacao: str = Field(default="DEPOSITO")  # DEPOSITO ou SAQUE


class CofreResposta(BaseModel):
    id: int
    usuario_id: int
    nome: str
    categoria: str
    valor_meta: Decimal
    saldo_atual: Decimal
    porcentagem_autoguarda: Decimal
    ativa: bool
    valor_restante: Decimal
    percentual_meta: Decimal
    data_criacao: datetime

    class Config:
        from_attributes = True
