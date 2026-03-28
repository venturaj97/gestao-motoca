from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel

from app.schemas.indicador import IndicadorResumoResposta
from app.schemas.meta import MetaAlertaResposta, MetaResposta


class VisaoMesResposta(BaseModel):
    ano: int
    mes: int
    periodo_inicio: date
    periodo_fim: date
    moto_usuario_id: Optional[int]

    ganho: IndicadorResumoResposta
    despesa: IndicadorResumoResposta
    saldo_mes: Decimal
    resumo_executivo: list[str]

    metas_ativas: list[MetaResposta]
    alertas_mensais: list[MetaAlertaResposta]
