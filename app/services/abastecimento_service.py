from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.abastecimento import Abastecimento
from app.models.categoria import Categoria
from app.schemas.abastecimento import AbastecimentoCriar
from app.schemas.lancamento import LancamentoCriar
from app.services.lancamento_service import (
    atualizar_lancamento,
    criar_lancamento,
    excluir_lancamento,
)


def _calcular_valor_litro(valor_total: Decimal, litros: Decimal) -> Decimal:
    if litros <= 0:
        raise ValueError("litros_invalidos")
    return valor_total / litros


def criar_abastecimento(db: Session, dados: AbastecimentoCriar) -> Abastecimento:
    # valida categoria (precisa ser DESPESA, normalmente combustivel)
    categoria = db.execute(
        select(Categoria).where(Categoria.id == dados.categoria_id)
    ).scalar_one_or_none()

    if not categoria:
        raise ValueError("categoria_nao_encontrada")

    if not categoria.ativo:
        raise ValueError("categoria_inativa")

    if categoria.tipo != "DESPESA":
        raise ValueError("categoria_nao_e_despesa")

    # cria lancamento de despesa vinculada ao abastecimento (resolver de moto dentro de criar_lancamento)
    lancamento_dados = LancamentoCriar(
        usuario_id=dados.usuario_id,
        categoria_id=dados.categoria_id,
        tipo="DESPESA",
        valor=dados.valor_total,
        descricao=dados.descricao,
        data_lancamento=dados.data_abastecimento or date.today(),
        moto_usuario_id=dados.moto_usuario_id,
    )

    try:
        lancamento = criar_lancamento(db, lancamento_dados, auto_commit=False)

        valor_litro = _calcular_valor_litro(dados.valor_total, dados.litros)

        abastecimento = Abastecimento(
            usuario_id=dados.usuario_id,
            moto_usuario_id=lancamento.moto_usuario_id,
            lancamento_id=lancamento.id,
            litros=dados.litros,
            valor_total=dados.valor_total,
            valor_litro=valor_litro,
            km_atual=dados.km_atual,
            data_abastecimento=lancamento.data_lancamento,
            posto=dados.posto,
            tipo_combustivel=dados.tipo_combustivel,
        )

        db.add(abastecimento)
        db.commit()
        db.refresh(abastecimento)
        return abastecimento
    except Exception:
        db.rollback()
        raise


def listar_abastecimentos(
    db: Session,
    usuario_id: int,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    moto_usuario_id: Optional[int] = None,
) -> list[Abastecimento]:
    stmt = (
        select(Abastecimento)
        .where(Abastecimento.usuario_id == usuario_id)
        .order_by(Abastecimento.data_abastecimento.desc(), Abastecimento.id.desc())
    )

    if data_inicio:
        stmt = stmt.where(Abastecimento.data_abastecimento >= data_inicio)

    if data_fim:
        stmt = stmt.where(Abastecimento.data_abastecimento <= data_fim)

    if moto_usuario_id:
        stmt = stmt.where(Abastecimento.moto_usuario_id == moto_usuario_id)

    return db.execute(stmt).scalars().all()


def atualizar_abastecimento(
    db: Session,
    abastecimento_id: int,
    dados: AbastecimentoCriar,
) -> Abastecimento:
    abastecimento = db.execute(
        select(Abastecimento).where(
            Abastecimento.id == abastecimento_id,
            Abastecimento.usuario_id == dados.usuario_id,
        )
    ).scalar_one_or_none()
    if not abastecimento:
        raise ValueError("abastecimento_nao_encontrado")

    categoria = db.execute(
        select(Categoria).where(Categoria.id == dados.categoria_id)
    ).scalar_one_or_none()

    if not categoria:
        raise ValueError("categoria_nao_encontrada")

    if not categoria.ativo:
        raise ValueError("categoria_inativa")

    if categoria.tipo != "DESPESA":
        raise ValueError("categoria_nao_e_despesa")

    lancamento_dados = LancamentoCriar(
        usuario_id=dados.usuario_id,
        categoria_id=dados.categoria_id,
        tipo="DESPESA",
        valor=dados.valor_total,
        descricao=dados.descricao,
        data_lancamento=dados.data_abastecimento or date.today(),
        moto_usuario_id=dados.moto_usuario_id,
    )

    try:
        lancamento = atualizar_lancamento(db, abastecimento.lancamento_id, lancamento_dados, auto_commit=False)
        valor_litro = _calcular_valor_litro(dados.valor_total, dados.litros)

        abastecimento.usuario_id = dados.usuario_id
        abastecimento.moto_usuario_id = lancamento.moto_usuario_id
        abastecimento.litros = dados.litros
        abastecimento.valor_total = dados.valor_total
        abastecimento.valor_litro = valor_litro
        abastecimento.km_atual = dados.km_atual
        abastecimento.data_abastecimento = lancamento.data_lancamento
        abastecimento.posto = dados.posto
        abastecimento.tipo_combustivel = dados.tipo_combustivel

        db.commit()
        db.refresh(abastecimento)
        return abastecimento
    except Exception:
        db.rollback()
        raise


def excluir_abastecimento(db: Session, abastecimento_id: int, usuario_id: int) -> None:
    abastecimento = db.execute(
        select(Abastecimento).where(
            Abastecimento.id == abastecimento_id,
            Abastecimento.usuario_id == usuario_id,
        )
    ).scalar_one_or_none()
    if not abastecimento:
        raise ValueError("abastecimento_nao_encontrado")

    try:
        excluir_lancamento(db, abastecimento.lancamento_id, usuario_id, auto_commit=False)
        db.commit()
    except Exception:
        db.rollback()
        raise
