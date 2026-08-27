import calendar
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.lancamento import Lancamento
from app.models.meta import Meta
from app.schemas.meta import MetaAtualizar, MetaCriar


def _normalizar_tipo(valor: str) -> str:
    tipo = valor.upper()
    if tipo not in {"GANHO", "DESPESA"}:
        raise ValueError("tipo_invalido")
    return tipo


def _normalizar_periodo(valor: str) -> str:
    periodo = valor.upper()
    if periodo not in {"DIARIO", "SEMANAL", "MENSAL", "OBJETIVO"}:
        raise ValueError("periodo_invalido")
    return periodo


def criar_meta(db: Session, usuario_id: int, dados: MetaCriar) -> Meta:
    meta = Meta(
        usuario_id=usuario_id,
        nome=dados.nome.strip(),
        tipo=_normalizar_tipo(dados.tipo),
        periodo=_normalizar_periodo(dados.periodo),
        valor_meta=dados.valor_meta,
        dias_trabalho_semana=dados.dias_trabalho_semana or 6,
        categoria_cofre=dados.categoria_cofre,
        ativa=dados.ativa,
    )
    db.add(meta)
    db.commit()
    db.refresh(meta)
    return meta


def listar_metas(db: Session, usuario_id: int, apenas_ativas: bool | None = None) -> list[Meta]:
    stmt = select(Meta).where(Meta.usuario_id == usuario_id).order_by(Meta.id.desc())
    if apenas_ativas is True:
        stmt = stmt.where(Meta.ativa == True)  # noqa: E712
    if apenas_ativas is False:
        stmt = stmt.where(Meta.ativa == False)  # noqa: E712
    return db.execute(stmt).scalars().all()


def atualizar_meta(db: Session, usuario_id: int, meta_id: int, dados: MetaAtualizar) -> Meta:
    meta = db.execute(
        select(Meta).where(
            Meta.id == meta_id,
            Meta.usuario_id == usuario_id,
        )
    ).scalar_one_or_none()
    if not meta:
        raise ValueError("meta_nao_encontrada")

    if dados.nome is not None:
        meta.nome = dados.nome.strip()
    if dados.tipo is not None:
        meta.tipo = _normalizar_tipo(dados.tipo)
    if dados.periodo is not None:
        meta.periodo = _normalizar_periodo(dados.periodo)
    if dados.valor_meta is not None:
        meta.valor_meta = dados.valor_meta
    if dados.dias_trabalho_semana is not None:
        meta.dias_trabalho_semana = dados.dias_trabalho_semana
    if dados.categoria_cofre is not None:
        meta.categoria_cofre = dados.categoria_cofre
    if dados.ativa is not None:
        meta.ativa = dados.ativa

    db.commit()
    db.refresh(meta)
    return meta


def excluir_meta(db: Session, usuario_id: int, meta_id: int) -> None:
    meta = db.execute(
        select(Meta).where(
            Meta.id == meta_id,
            Meta.usuario_id == usuario_id,
        )
    ).scalar_one_or_none()
    if not meta:
        raise ValueError("meta_nao_encontrada")

    db.delete(meta)
    db.commit()


def _inicio_fim_periodo(data_ref: date, periodo: str) -> tuple[date, date]:
    if periodo == "DIARIO":
        return data_ref, data_ref

    if periodo == "SEMANAL":
        inicio = data_ref - timedelta(days=data_ref.weekday())
        fim = inicio + timedelta(days=6)
        return inicio, fim

    if periodo == "MENSAL":
        inicio = date(data_ref.year, data_ref.month, 1)
        ultimo_dia = calendar.monthrange(data_ref.year, data_ref.month)[1]
        fim = date(data_ref.year, data_ref.month, ultimo_dia)
        return inicio, fim

    # OBJETIVO (meta global/acumulada sem prazo fixo)
    inicio = date(2000, 1, 1)
    fim = date(2099, 12, 31)
    return inicio, fim


def _status_meta(tipo: str, realizado: Decimal, valor_meta: Decimal, progresso_periodo: Decimal, meta_diaria: Decimal, dias_restantes: int) -> tuple[str, str]:
    if tipo == "GANHO":
        if realizado >= valor_meta:
            return "atingida", "Meta de ganho batida! Excelente trabalho."
        if dias_restantes > 0 and meta_diaria > 0:
            return "em_andamento", f"Faltam {dias_restantes} dias de trampo. Meta necessária: R$ {meta_diaria:.2f}/dia."
        return "em_andamento", "Meta de ganho em andamento."

    # DESPESA
    if realizado > valor_meta:
        return "estourada", f"Atenção: Teto de despesas ultrapassado em R$ {realizado - valor_meta:.2f}."
    if realizado >= valor_meta * Decimal("0.85"):
        return "atencao", "Gastos próximos do limite estabelecido."
    return "dentro_meta", "Despesas sob controle dentro da meta."


def listar_alertas_metas(db: Session, usuario_id: int, data_ref: date | None = None) -> list[dict]:
    hoje = data_ref or date.today()
    metas_ativas = db.execute(
        select(Meta).where(
            Meta.usuario_id == usuario_id,
            Meta.ativa == True,  # noqa: E712
            Meta.periodo != "OBJETIVO",
        )
    ).scalars().all()

    alertas: list[dict] = []
    for meta in metas_ativas:
        inicio, fim = _inicio_fim_periodo(hoje, meta.periodo)

        realizado_raw = db.execute(
            select(func.coalesce(func.sum(Lancamento.valor), 0)).where(
                Lancamento.usuario_id == usuario_id,
                Lancamento.tipo == meta.tipo,
                Lancamento.data_lancamento >= inicio,
                Lancamento.data_lancamento <= hoje,
            )
        ).scalar_one()

        realizado = Decimal(realizado_raw or 0)
        valor_meta = Decimal(meta.valor_meta)
        valor_restante = max(Decimal("0"), valor_meta - realizado)

        # Cálculo de dias de trabalho restantes no período
        dias_trabalho_total = meta.dias_trabalho_semana or 6
        if meta.periodo == "DIARIO":
            dias_totais = 1
            dias_corridos = 1
            dias_restantes = 0 if realizado >= valor_meta else 1
        elif meta.periodo == "SEMANAL":
            dias_totais = 7
            dias_corridos = (hoje - inicio).days + 1
            dias_restantes = max(1, dias_trabalho_total - (dias_corridos - 1))
        elif meta.periodo == "MENSAL":
            dias_totais = (fim - inicio).days + 1
            dias_corridos = (hoje - inicio).days + 1
            # Proporção mensal de dias de trabalho
            dias_restantes = max(1, int((dias_totais - dias_corridos + 1) * (dias_trabalho_total / 7.0)))
        else:
            dias_totais = 30
            dias_corridos = 1
            dias_restantes = 30

        progresso_periodo = Decimal(dias_corridos) / Decimal(dias_totais)
        percentual_meta = Decimal("0")
        if valor_meta > 0:
            percentual_meta = min(Decimal("100"), (realizado / valor_meta) * Decimal("100"))

        meta_diaria_necessaria = Decimal("0")
        if valor_restante > 0 and dias_restantes > 0:
            meta_diaria_necessaria = round(valor_restante / Decimal(dias_restantes), 2)

        status, recomendacao = _status_meta(meta.tipo, realizado, valor_meta, progresso_periodo, meta_diaria_necessaria, dias_restantes)

        alertas.append(
            {
                "meta_id": meta.id,
                "nome": meta.nome,
                "tipo": meta.tipo,
                "periodo": meta.periodo,
                "valor_meta": valor_meta,
                "dias_trabalho_semana": meta.dias_trabalho_semana or 6,
                "categoria_cofre": meta.categoria_cofre,
                "periodo_inicio": inicio,
                "periodo_fim": fim,
                "realizado": realizado,
                "valor_restante": valor_restante,
                "meta_diaria_necessaria": meta_diaria_necessaria,
                "dias_trabalho_restantes": dias_restantes,
                "progresso_periodo_percentual": round(progresso_periodo * Decimal("100"), 1),
                "percentual_meta": round(percentual_meta, 1),
                "status": status,
                "recomendacao": recomendacao,
            }
        )
    return alertas
