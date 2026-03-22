from datetime import date
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.categoria import Categoria
from app.models.lancamento import Lancamento
from app.models.moto_usuario import MotoUsuario
from app.schemas.lancamento import LancamentoCriar


def _resolver_moto_do_lancamento(
    db: Session,
    usuario_id: int,
    moto_usuario_id_opcional: Optional[int],
) -> int:
    """
    Regra: precisa existir moto cadastrada; com 1 moto ativa e sem id no body, usa ela;
    com 2+ motos ativas e sem id, obriga informar qual moto.
    """
    if moto_usuario_id_opcional is not None:
        moto = db.execute(
            select(MotoUsuario).where(
                MotoUsuario.id == moto_usuario_id_opcional,
                MotoUsuario.usuario_id == usuario_id,
            )
        ).scalar_one_or_none()
        if not moto:
            raise ValueError("moto_nao_encontrada_ou_nao_sua")
        return moto.id

    qtd_total = db.execute(
        select(func.count()).select_from(MotoUsuario).where(MotoUsuario.usuario_id == usuario_id)
    ).scalar_one()
    if qtd_total == 0:
        raise ValueError("usuario_sem_moto")

    qtd_ativas = db.execute(
        select(func.count())
        .select_from(MotoUsuario)
        .where(MotoUsuario.usuario_id == usuario_id, MotoUsuario.ativa == True)  # noqa: E712
    ).scalar_one()
    if qtd_ativas == 0:
        raise ValueError("nenhuma_moto_ativa")

    if qtd_ativas == 1:
        unica = db.execute(
            select(MotoUsuario).where(
                MotoUsuario.usuario_id == usuario_id,
                MotoUsuario.ativa == True,  # noqa: E712
            )
        ).scalar_one()
        return unica.id

    raise ValueError("moto_obrigatoria_informar")


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

    moto_id = _resolver_moto_do_lancamento(db, dados.usuario_id, dados.moto_usuario_id)

    lancamento = Lancamento(
        usuario_id=dados.usuario_id,
        categoria_id=dados.categoria_id,
        moto_usuario_id=moto_id,
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
