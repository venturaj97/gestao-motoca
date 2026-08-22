import calendar
from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.abastecimento import Abastecimento
from app.services.indicador_service import obter_indicadores_resumo


def _intervalo_mes(ano: int, mes: int) -> tuple[date, date]:
    inicio = date(ano, mes, 1)
    ultimo_dia = calendar.monthrange(ano, mes)[1]
    fim = date(ano, mes, ultimo_dia)
    return inicio, fim


def _mes_anterior(ano: int, mes: int) -> tuple[int, int]:
    if mes == 1:
        return ano - 1, 12
    return ano, mes - 1


def _calcular_variacao(atual: Decimal, anterior: Decimal) -> Optional[float]:
    if anterior == 0:
        return None
    return round(float((atual - anterior) / anterior * 100), 1)


def obter_comparativo_mensal(
    db: Session,
    usuario_id: int,
    ano: int,
    mes: int,
    moto_usuario_id: Optional[int] = None,
) -> dict:
    inicio_atual, fim_atual = _intervalo_mes(ano, mes)
    ano_ant, mes_ant = _mes_anterior(ano, mes)
    inicio_ant, fim_ant = _intervalo_mes(ano_ant, mes_ant)

    ganho_atual = obter_indicadores_resumo(db, usuario_id, "GANHO", inicio_atual, fim_atual, moto_usuario_id)
    despesa_atual = obter_indicadores_resumo(db, usuario_id, "DESPESA", inicio_atual, fim_atual, moto_usuario_id)

    ganho_ant = obter_indicadores_resumo(db, usuario_id, "GANHO", inicio_ant, fim_ant, moto_usuario_id)
    despesa_ant = obter_indicadores_resumo(db, usuario_id, "DESPESA", inicio_ant, fim_ant, moto_usuario_id)

    fat_atual = Decimal(ganho_atual["total_periodo"])
    fat_ant = Decimal(ganho_ant["total_periodo"])
    desp_atual = Decimal(despesa_atual["total_periodo"])
    desp_ant = Decimal(despesa_ant["total_periodo"])
    lucro_atual = fat_atual - desp_atual
    lucro_ant = fat_ant - desp_ant

    var_fat = _calcular_variacao(fat_atual, fat_ant)
    var_desp = _calcular_variacao(desp_atual, desp_ant)
    var_lucro = _calcular_variacao(lucro_atual, lucro_ant)

    return {
        "faturamento": {
            "label": "Faturamento",
            "valor_atual": fat_atual,
            "valor_anterior": fat_ant,
            "variacao_percentual": var_fat,
            "positivo": var_fat is None or var_fat >= 0,
        },
        "despesas": {
            "label": "Despesas",
            "valor_atual": desp_atual,
            "valor_anterior": desp_ant,
            "variacao_percentual": var_desp,
            "positivo": var_desp is None or var_desp <= 0,
        },
        "lucro": {
            "label": "Lucro Real",
            "valor_atual": lucro_atual,
            "valor_anterior": lucro_ant,
            "variacao_percentual": var_lucro,
            "positivo": lucro_atual >= 0,
        },
        "ganho_atual": ganho_atual,
        "despesa_atual": despesa_atual,
    }


def obter_eficiencia_combustivel(
    db: Session,
    usuario_id: int,
    ano: int,
    mes: int,
    moto_usuario_id: Optional[int] = None,
) -> dict:
    inicio, fim = _intervalo_mes(ano, mes)

    filtros = [
        Abastecimento.usuario_id == usuario_id,
        Abastecimento.data_abastecimento >= inicio,
        Abastecimento.data_abastecimento <= fim,
    ]
    if moto_usuario_id:
        filtros.append(Abastecimento.moto_usuario_id == moto_usuario_id)

    abastecimentos = db.execute(
        select(Abastecimento)
        .where(*filtros)
        .order_by(Abastecimento.data_abastecimento.asc(), Abastecimento.id.asc())
    ).scalars().all()

    if len(abastecimentos) < 2:
        total_litros = sum(float(a.litros) for a in abastecimentos)
        total_gasto = sum(Decimal(str(a.valor_total)) for a in abastecimentos)
        return {
            "km_por_litro": None,
            "custo_por_km": None,
            "total_litros": total_litros,
            "total_gasto_combustivel": total_gasto,
            "km_rodados_combustivel": 0,
            "dados_suficientes": False,
        }

    com_km = [a for a in abastecimentos if a.km_atual is not None and a.km_atual > 0]

    total_litros = sum(float(a.litros) for a in abastecimentos)
    total_gasto = sum(Decimal(str(a.valor_total)) for a in abastecimentos)

    if len(com_km) >= 2:
        km_primeiro = com_km[0].km_atual
        km_ultimo = com_km[-1].km_atual
        km_rodados = km_ultimo - km_primeiro
        litros_entre = sum(float(a.litros) for a in com_km[1:])

        if km_rodados > 0 and litros_entre > 0:
            km_por_litro = round(km_rodados / litros_entre, 1)
            custo_por_km = round(float(total_gasto) / km_rodados, 2) if km_rodados > 0 else None
            return {
                "km_por_litro": km_por_litro,
                "custo_por_km": custo_por_km,
                "total_litros": total_litros,
                "total_gasto_combustivel": total_gasto,
                "km_rodados_combustivel": km_rodados,
                "dados_suficientes": True,
            }

    return {
        "km_por_litro": None,
        "custo_por_km": None,
        "total_litros": total_litros,
        "total_gasto_combustivel": total_gasto,
        "km_rodados_combustivel": 0,
        "dados_suficientes": False,
    }


def _gerar_insights(
    comparativo: dict,
    ganho: dict,
    despesa: dict,
    eficiencia: dict,
) -> list[str]:
    insights: list[str] = []

    var_lucro = comparativo["lucro"]["variacao_percentual"]
    if var_lucro is not None:
        if var_lucro > 0:
            insights.append(f"Seu lucro cresceu {var_lucro}% em relação ao mês anterior.")
        elif var_lucro < 0:
            insights.append(f"Seu lucro caiu {abs(var_lucro)}% em relação ao mês anterior.")
        else:
            insights.append("Seu lucro se manteve estável em relação ao mês anterior.")

    melhor_dia = ganho.get("melhor_dia_semana")
    if melhor_dia:
        dias_pt = {
            "SEGUNDA": "Segunda-feira", "TERCA": "Terça-feira", "QUARTA": "Quarta-feira",
            "QUINTA": "Quinta-feira", "SEXTA": "Sexta-feira", "SABADO": "Sábado", "DOMINGO": "Domingo",
        }
        nome_dia = dias_pt.get(melhor_dia["dia_semana"], melhor_dia["dia_semana"])
        total_dia = Decimal(melhor_dia["total"])
        insights.append(f"{nome_dia} é seu melhor dia: R$ {total_dia:.2f} de faturamento.")

    despesas_cat = despesa.get("despesas_por_categoria", [])
    if despesas_cat:
        vilao = despesas_cat[0]
        total_desp = Decimal(despesa.get("total_periodo", "0"))
        if total_desp > 0:
            pct = round(float(Decimal(vilao["total"]) / total_desp * 100), 0)
            insights.append(f"{vilao['categoria_nome']} é seu maior gasto: {pct:.0f}% das despesas.")

    if eficiencia.get("dados_suficientes") and eficiencia.get("km_por_litro"):
        insights.append(f"Sua moto faz {eficiencia['km_por_litro']} km/L neste mês.")

    if eficiencia.get("custo_por_km"):
        insights.append(f"Cada km rodado custa R$ {eficiencia['custo_por_km']:.2f} em combustível.")

    return insights


def obter_inteligencia_resumo(
    db: Session,
    usuario_id: int,
    ano: int,
    mes: int,
    moto_usuario_id: Optional[int] = None,
) -> dict:
    comp = obter_comparativo_mensal(db, usuario_id, ano, mes, moto_usuario_id)

    ganho_atual = comp.pop("ganho_atual")
    despesa_atual = comp.pop("despesa_atual")

    ranking_ganho = ganho_atual.get("resumo_dia_semana", [])
    ranking_despesa = despesa_atual.get("resumo_dia_semana", [])
    despesas_cat = despesa_atual.get("despesas_por_categoria", [])

    total_ganho = Decimal(ganho_atual.get("total_periodo", "0"))
    total_despesa = Decimal(despesa_atual.get("total_periodo", "0"))

    for item in ranking_ganho:
        item["percentual"] = round(float(Decimal(item["total"]) / total_ganho * 100), 1) if total_ganho > 0 else 0.0
    for item in ranking_despesa:
        item["percentual"] = round(float(Decimal(item["total"]) / total_despesa * 100), 1) if total_despesa > 0 else 0.0

    for item in despesas_cat:
        item["percentual"] = round(float(Decimal(item["total"]) / total_despesa * 100), 1) if total_despesa > 0 else 0.0

    ranking_ganho_sorted = sorted(ranking_ganho, key=lambda x: Decimal(x["total"]), reverse=True)
    despesas_cat_sorted = sorted(despesas_cat, key=lambda x: Decimal(x["total"]), reverse=True)

    maior_vilao = despesas_cat_sorted[0] if despesas_cat_sorted else None

    ticket_medio = Decimal("0")
    qtd_desp = despesa_atual.get("quantidade_lancamentos", 0)
    if qtd_desp > 0:
        ticket_medio = total_despesa / Decimal(qtd_desp)

    eficiencia = obter_eficiencia_combustivel(db, usuario_id, ano, mes, moto_usuario_id)

    insights = _gerar_insights(comp, ganho_atual, despesa_atual, eficiencia)

    return {
        "ano": ano,
        "mes": mes,
        "comparativo": comp,
        "ranking_dias_ganho": ranking_ganho_sorted,
        "ranking_dias_despesa": ranking_despesa,
        "despesas_por_categoria": despesas_cat_sorted,
        "maior_vilao": maior_vilao,
        "ticket_medio_despesa": ticket_medio,
        "eficiencia_combustivel": eficiencia,
        "insights": insights,
    }
