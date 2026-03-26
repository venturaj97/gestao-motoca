from datetime import date
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.categoria import Categoria
from app.models.manutencao import Manutencao
from app.schemas.lancamento import LancamentoCriar
from app.schemas.manutencao import ManutencaoCriar
from app.services.lancamento_service import (
    atualizar_lancamento,
    criar_lancamento,
    excluir_lancamento,
)


def criar_manutencao(db: Session, dados: ManutencaoCriar) -> Manutencao:
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
        data_lancamento=dados.data_manutencao or date.today(),
        moto_usuario_id=dados.moto_usuario_id,
    )

    lancamento = criar_lancamento(db, lancamento_dados)

    manutencao = Manutencao(
        usuario_id=dados.usuario_id,
        moto_usuario_id=lancamento.moto_usuario_id,
        lancamento_id=lancamento.id,
        valor_total=dados.valor_total,
        km_atual=dados.km_atual,
        data_manutencao=lancamento.data_lancamento,
        descricao_servico=dados.descricao_servico,
        oficina=dados.oficina,
        tipo_servico=dados.tipo_servico,
    )

    db.add(manutencao)
    db.commit()
    db.refresh(manutencao)

    return manutencao


def listar_manutencoes(
    db: Session,
    usuario_id: int,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    moto_usuario_id: Optional[int] = None,
) -> list[Manutencao]:
    stmt = (
        select(Manutencao)
        .where(Manutencao.usuario_id == usuario_id)
        .order_by(Manutencao.data_manutencao.desc(), Manutencao.id.desc())
    )

    if data_inicio:
        stmt = stmt.where(Manutencao.data_manutencao >= data_inicio)

    if data_fim:
        stmt = stmt.where(Manutencao.data_manutencao <= data_fim)

    if moto_usuario_id:
        stmt = stmt.where(Manutencao.moto_usuario_id == moto_usuario_id)

    return db.execute(stmt).scalars().all()


def atualizar_manutencao(
    db: Session,
    manutencao_id: int,
    dados: ManutencaoCriar,
) -> Manutencao:
    manutencao = db.execute(
        select(Manutencao).where(
            Manutencao.id == manutencao_id,
            Manutencao.usuario_id == dados.usuario_id,
        )
    ).scalar_one_or_none()
    if not manutencao:
        raise ValueError("manutencao_nao_encontrada")

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
        data_lancamento=dados.data_manutencao or date.today(),
        moto_usuario_id=dados.moto_usuario_id,
    )

    lancamento = atualizar_lancamento(db, manutencao.lancamento_id, lancamento_dados)

    manutencao.usuario_id = dados.usuario_id
    manutencao.moto_usuario_id = lancamento.moto_usuario_id
    manutencao.valor_total = dados.valor_total
    manutencao.km_atual = dados.km_atual
    manutencao.data_manutencao = lancamento.data_lancamento
    manutencao.descricao_servico = dados.descricao_servico
    manutencao.oficina = dados.oficina
    manutencao.tipo_servico = dados.tipo_servico

    db.commit()
    db.refresh(manutencao)
    return manutencao


def excluir_manutencao(db: Session, manutencao_id: int, usuario_id: int) -> None:
    manutencao = db.execute(
        select(Manutencao).where(
            Manutencao.id == manutencao_id,
            Manutencao.usuario_id == usuario_id,
        )
    ).scalar_one_or_none()
    if not manutencao:
        raise ValueError("manutencao_nao_encontrada")

    excluir_lancamento(db, manutencao.lancamento_id, usuario_id)
