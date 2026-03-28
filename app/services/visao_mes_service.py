import calendar
from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from app.services.indicador_service import obter_indicadores_resumo
from app.services.meta_service import listar_alertas_metas, listar_metas


def _intervalo_mes(ano: int, mes: int) -> tuple[date, date]:
    inicio = date(ano, mes, 1)
    ultimo_dia = calendar.monthrange(ano, mes)[1]
    fim = date(ano, mes, ultimo_dia)
    return inicio, fim


def _data_referencia_para_mes(inicio: date, fim: date) -> date:
    hoje = date.today()
    if hoje < inicio:
        return inicio
    if hoje > fim:
        return fim
    return hoje


def obter_visao_mes(
    db: Session,
    usuario_id: int,
    ano: int,
    mes: int,
    moto_usuario_id: Optional[int] = None,
) -> dict:
    inicio, fim = _intervalo_mes(ano, mes)

    ganho = obter_indicadores_resumo(
        db=db,
        usuario_id=usuario_id,
        tipo="GANHO",
        data_inicio=inicio,
        data_fim=fim,
        moto_usuario_id=moto_usuario_id,
    )
    despesa = obter_indicadores_resumo(
        db=db,
        usuario_id=usuario_id,
        tipo="DESPESA",
        data_inicio=inicio,
        data_fim=fim,
        moto_usuario_id=moto_usuario_id,
    )

    saldo_mes = Decimal(ganho["total_periodo"]) - Decimal(despesa["total_periodo"])

    metas_ativas = listar_metas(db, usuario_id=usuario_id, apenas_ativas=True)
    data_ref = _data_referencia_para_mes(inicio, fim)
    alertas = listar_alertas_metas(db, usuario_id=usuario_id, data_ref=data_ref)
    alertas_mensais = [
        alerta
        for alerta in alertas
        if alerta["periodo"] == "MENSAL"
        and alerta["periodo_inicio"] == inicio
        and alerta["periodo_fim"] == fim
    ]

    return {
        "ano": ano,
        "mes": mes,
        "periodo_inicio": inicio,
        "periodo_fim": fim,
        "moto_usuario_id": moto_usuario_id,
        "ganho": ganho,
        "despesa": despesa,
        "saldo_mes": saldo_mes,
        "metas_ativas": metas_ativas,
        "alertas_mensais": alertas_mensais,
    }
