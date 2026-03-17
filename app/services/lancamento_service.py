from datetime import date
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.categoria import Categoria
from app.models.lancamento import Lancamento
from app.schemas.lancamento import LancamentoCriar


def criar_lancamento(db: Session, dados: LancamentoCriar) -> Lancamento:
    tipo = dados.tipo.upper()

    # valida tipo
    if tipo not in ["GANHO", "DESPESA"]:
        raise ValueError("tipo_invalido")

    # valida categoria
    categoria = db.execute(
        select(Categoria).where(Categoria.id == dados.categoria_id)
    ).scalar_one_or_none()

    if not categoria:
        raise ValueError("categoria_nao_encontrada")

    if not categoria.ativo:
        raise ValueError("categoria_inativa")

    # tipo do lançamento deve bater com tipo da categoria
    if tipo != categoria.tipo:
        raise ValueError("tipo_incompativel_com_categoria")

    lancamento = Lancamento(
        usuario_id=dados.usuario_id,
        categoria_id=dados.categoria_id,
        moto_usuario_id=dados.moto_usuario_id,
        tipo=tipo,
        valor=dados.valor,
        descricao=dados.descricao,
        data_lancamento=dados.data_lancamento or date.today(),
    )

    db.add(lancamento)
    db.commit()
    db.refresh(lancamento)

    return lancamento


def listar_lancamentos(
    db: Session,
    usuario_id: int,
    tipo: Optional[str] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
) -> list[Lancamento]:
    stmt = (
        select(Lancamento)
        .where(Lancamento.usuario_id == usuario_id)
        .order_by(Lancamento.data_lancamento.desc(), Lancamento.id.desc())
    )

    if tipo:
        stmt = stmt.where(Lancamento.tipo == tipo.upper())

    if data_inicio:
        stmt = stmt.where(Lancamento.data_lancamento >= data_inicio)

    if data_fim:
        stmt = stmt.where(Lancamento.data_lancamento <= data_fim)

    return db.execute(stmt).scalars().all()
