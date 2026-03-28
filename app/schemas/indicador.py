from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class IndicadorDiaSemanaItem(BaseModel):
    dia_semana: str
    total: Decimal
    quantidade: int


class IndicadorCalendarioItem(BaseModel):
    data: date
    total: Decimal
    quantidade: int


class IndicadorPeriodoGanhoItem(BaseModel):
    periodo: str
    total: Decimal
    quantidade: int


class IndicadorResumoResposta(BaseModel):
    tipo: str
    data_inicio: Optional[date]
    data_fim: Optional[date]
    moto_usuario_id: Optional[int]

    total_periodo: Decimal
    melhor_dia_semana: Optional[IndicadorDiaSemanaItem]
    resumo_dia_semana: list[IndicadorDiaSemanaItem]
    calendario_periodo: list[IndicadorCalendarioItem]
    ganhos_por_periodo: list[IndicadorPeriodoGanhoItem]
