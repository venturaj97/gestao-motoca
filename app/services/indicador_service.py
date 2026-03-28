from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models.categoria import Categoria
from app.models.lancamento import Lancamento


def _validar_tipo(tipo: str) -> str:
    tipo_normalizado = tipo.upper()
    if tipo_normalizado not in {"GANHO", "DESPESA"}:
        raise ValueError("tipo_invalido")
    return tipo_normalizado


def _validar_intervalo(data_inicio: Optional[date], data_fim: Optional[date]) -> None:
    if data_inicio and data_fim and data_inicio > data_fim:
        raise ValueError("intervalo_invalido")


def _filtros_base(
    usuario_id: int,
    tipo: str,
    data_inicio: Optional[date],
    data_fim: Optional[date],
    moto_usuario_id: Optional[int],
):
    filtros = [Lancamento.usuario_id == usuario_id, Lancamento.tipo == tipo]
    if data_inicio:
        filtros.append(Lancamento.data_lancamento >= data_inicio)
    if data_fim:
        filtros.append(Lancamento.data_lancamento <= data_fim)
    if moto_usuario_id:
        filtros.append(Lancamento.moto_usuario_id == moto_usuario_id)
    return filtros


def _ordem_dia_semana_expr():
    return case(
        (Lancamento.dia_semana == "SEGUNDA", 1),
        (Lancamento.dia_semana == "TERCA", 2),
        (Lancamento.dia_semana == "QUARTA", 3),
        (Lancamento.dia_semana == "QUINTA", 4),
        (Lancamento.dia_semana == "SEXTA", 5),
        (Lancamento.dia_semana == "SABADO", 6),
        (Lancamento.dia_semana == "DOMINGO", 7),
        else_=99,
    )


def _obter_total_periodo(db: Session, filtros) -> Decimal:
    stmt = select(func.coalesce(func.sum(Lancamento.valor), 0)).where(*filtros)
    total = db.execute(stmt).scalar_one()
    return Decimal(total or 0)


def _obter_quantidade_lancamentos(db: Session, filtros) -> int:
    stmt = select(func.count(Lancamento.id)).where(*filtros)
    return int(db.execute(stmt).scalar_one() or 0)


def _obter_resumo_dia_semana(db: Session, filtros) -> list[dict]:
    stmt = (
        select(
            Lancamento.dia_semana.label("dia_semana"),
            func.coalesce(func.sum(Lancamento.valor), 0).label("total"),
            func.count(Lancamento.id).label("quantidade"),
        )
        .where(*filtros, Lancamento.dia_semana.is_not(None))
        .group_by(Lancamento.dia_semana)
        .order_by(_ordem_dia_semana_expr())
    )
    return [
        {
            "dia_semana": row.dia_semana,
            "total": Decimal(row.total or 0),
            "quantidade": int(row.quantidade or 0),
        }
        for row in db.execute(stmt).all()
    ]


def _obter_melhor_dia_semana(resumo_dia_semana: list[dict]) -> Optional[dict]:
    if not resumo_dia_semana:
        return None
    return max(resumo_dia_semana, key=lambda item: (item["total"], item["quantidade"]))


def _obter_pior_dia_semana(resumo_dia_semana: list[dict]) -> Optional[dict]:
    if not resumo_dia_semana:
        return None
    return min(resumo_dia_semana, key=lambda item: (item["total"], item["quantidade"]))


def _obter_calendario_periodo(db: Session, filtros) -> list[dict]:
    stmt = (
        select(
            Lancamento.data_lancamento.label("data"),
            func.coalesce(func.sum(Lancamento.valor), 0).label("total"),
            func.count(Lancamento.id).label("quantidade"),
        )
        .where(*filtros)
        .group_by(Lancamento.data_lancamento)
        .order_by(Lancamento.data_lancamento.asc())
    )
    return [
        {
            "data": row.data,
            "total": Decimal(row.total or 0),
            "quantidade": int(row.quantidade or 0),
        }
        for row in db.execute(stmt).all()
    ]


def _obter_ganhos_por_periodo(db: Session, filtros, tipo: str) -> list[dict]:
    if tipo != "GANHO":
        return []
    stmt = (
        select(
            Lancamento.periodo.label("periodo"),
            func.coalesce(func.sum(Lancamento.valor), 0).label("total"),
            func.count(Lancamento.id).label("quantidade"),
        )
        .where(*filtros, Lancamento.periodo.is_not(None))
        .group_by(Lancamento.periodo)
        .order_by(func.sum(Lancamento.valor).desc())
    )
    return [
        {
            "periodo": row.periodo,
            "total": Decimal(row.total or 0),
            "quantidade": int(row.quantidade or 0),
        }
        for row in db.execute(stmt).all()
    ]


def _obter_despesas_por_categoria(db: Session, filtros, tipo: str) -> list[dict]:
    if tipo != "DESPESA":
        return []
    stmt = (
        select(
            Categoria.id.label("categoria_id"),
            Categoria.nome.label("categoria_nome"),
            func.coalesce(func.sum(Lancamento.valor), 0).label("total"),
            func.count(Lancamento.id).label("quantidade"),
        )
        .join(Categoria, Categoria.id == Lancamento.categoria_id)
        .where(*filtros)
        .group_by(Categoria.id, Categoria.nome)
        .order_by(func.sum(Lancamento.valor).desc())
    )
    return [
        {
            "categoria_id": int(row.categoria_id),
            "categoria_nome": row.categoria_nome,
            "total": Decimal(row.total or 0),
            "quantidade": int(row.quantidade or 0),
        }
        for row in db.execute(stmt).all()
    ]


def obter_indicadores_resumo(
    db: Session,
    usuario_id: int,
    tipo: str,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    moto_usuario_id: Optional[int] = None,
) -> dict:
    tipo_normalizado = _validar_tipo(tipo)
    _validar_intervalo(data_inicio, data_fim)
    filtros = _filtros_base(usuario_id, tipo_normalizado, data_inicio, data_fim, moto_usuario_id)

    total_periodo = _obter_total_periodo(db, filtros)
    quantidade_lancamentos = _obter_quantidade_lancamentos(db, filtros)
    ticket_medio = Decimal("0")
    if quantidade_lancamentos > 0:
        ticket_medio = total_periodo / Decimal(quantidade_lancamentos)
    resumo_dia_semana = _obter_resumo_dia_semana(db, filtros)
    melhor_dia_semana = _obter_melhor_dia_semana(resumo_dia_semana)
    pior_dia_semana = _obter_pior_dia_semana(resumo_dia_semana)
    calendario_periodo = _obter_calendario_periodo(db, filtros)
    ganhos_por_periodo = _obter_ganhos_por_periodo(db, filtros, tipo_normalizado)
    despesas_por_categoria = _obter_despesas_por_categoria(db, filtros, tipo_normalizado)

    return {
        "tipo": tipo_normalizado,
        "data_inicio": data_inicio,
        "data_fim": data_fim,
        "moto_usuario_id": moto_usuario_id,
        "total_periodo": total_periodo,
        "quantidade_lancamentos": quantidade_lancamentos,
        "ticket_medio": ticket_medio,
        "melhor_dia_semana": melhor_dia_semana,
        "pior_dia_semana": pior_dia_semana,
        "resumo_dia_semana": resumo_dia_semana,
        "calendario_periodo": calendario_periodo,
        "ganhos_por_periodo": ganhos_por_periodo,
        "despesas_por_categoria": despesas_por_categoria,
    }
