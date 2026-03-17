from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class LancamentoCriar(BaseModel):
    usuario_id: int
    categoria_id: int
    tipo: str
    valor: Decimal = Field(gt=0, decimal_places=2)
    descricao: Optional[str] = Field(default=None, max_length=255)
    data_lancamento: Optional[datetime] = None
    moto_usuario_id: Optional[int] = None


class LancamentoResposta(BaseModel):
    id: int
    usuario_id: int
    categoria_id: int
    moto_usuario_id: Optional[int]
    tipo: str
    valor: Decimal
    descricao: Optional[str]
    data_lancamento: datetime
    data_criacao: datetime

    class Config:
        from_attributes = True
