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


def _montar_resumo_executivo(
    ganho: dict,
    despesa: dict,
    saldo_mes: Decimal,
    alertas_mensais: list[dict],
) -> list[str]:
    mensagens: list[str] = []

    total_ganho = Decimal(ganho["total_periodo"])
    total_despesa = Decimal(despesa["total_periodo"])

    if saldo_mes > 0:
        mensagens.append(f"Saldo positivo no mes: R$ {saldo_mes:.2f}.")
    elif saldo_mes < 0:
        mensagens.append(f"Saldo negativo no mes: R$ {abs(saldo_mes):.2f}.")
    else:
        mensagens.append("Saldo do mes esta zerado.")

    if total_ganho > 0:
        relacao = (total_despesa / total_ganho) * Decimal("100")
        mensagens.append(f"Despesas representam {relacao:.1f}% dos ganhos do mes.")
    else:
        mensagens.append("Ainda nao ha ganhos registrados no mes para comparar despesas.")

    melhor_ganho = ganho.get("melhor_dia_semana")
    if melhor_ganho:
        mensagens.append(
            f"Melhor dia de ganho: {melhor_ganho['dia_semana']} (R$ {Decimal(melhor_ganho['total']):.2f})."
        )

    melhor_despesa = despesa.get("melhor_dia_semana")
    if melhor_despesa:
        mensagens.append(
            f"Dia com maior despesa: {melhor_despesa['dia_semana']} (R$ {Decimal(melhor_despesa['total']):.2f})."
        )

    qtd_alertas_criticos = sum(1 for alerta in alertas_mensais if alerta["status"] in {"estourada", "atencao"})
    if qtd_alertas_criticos > 0:
        mensagens.append(f"Voce possui {qtd_alertas_criticos} alerta(s) mensal(is) que exigem atencao.")
    else:
        mensagens.append("Nao ha alertas mensais criticos no momento.")

    return mensagens


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
    resumo_executivo = _montar_resumo_executivo(ganho, despesa, saldo_mes, alertas_mensais)

    return {
        "ano": ano,
        "mes": mes,
        "periodo_inicio": inicio,
        "periodo_fim": fim,
        "moto_usuario_id": moto_usuario_id,
        "ganho": ganho,
        "despesa": despesa,
        "saldo_mes": saldo_mes,
        "resumo_executivo": resumo_executivo,
        "metas_ativas": metas_ativas,
        "alertas_mensais": alertas_mensais,
    }
