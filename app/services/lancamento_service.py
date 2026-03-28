from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.abastecimento import Abastecimento
from app.models.categoria import Categoria
from app.models.lancamento import Lancamento
from app.models.manutencao import Manutencao
from app.models.moto_usuario import MotoUsuario
from app.schemas.lancamento import LancamentoCriar

PERIODOS_GANHO = {"DIARIO", "SEMANAL", "CORRIDA"}
DIAS_SEMANA = ["SEGUNDA", "TERCA", "QUARTA", "QUINTA", "SEXTA", "SABADO", "DOMINGO"]


def _dia_semana_por_data(data_ref: date) -> str:
    # date.weekday(): 0 = segunda ... 6 = domingo
    return DIAS_SEMANA[data_ref.weekday()]


def _resolver_campos_ganho(dados: LancamentoCriar, tipo: str) -> tuple[Optional[str], Optional[int], Optional[Decimal]]:
    periodo = dados.periodo.upper() if dados.periodo else None
    minutos = dados.minutos_corrida
    km = dados.km_corrida

    if tipo == "DESPESA":
        if periodo or minutos is not None or km is not None:
            raise ValueError("campos_ganho_nao_permitidos_para_despesa")
        return None, None, None

    # GANHO
    if not periodo:
        raise ValueError("periodo_obrigatorio")

    if periodo not in PERIODOS_GANHO:
        raise ValueError("periodo_invalido")

    if periodo == "CORRIDA":
        if minutos is None or km is None:
            raise ValueError("dados_corrida_obrigatorios")
        return periodo, minutos, km

    if minutos is not None or km is not None:
        raise ValueError("dados_corrida_nao_permitidos")
    return periodo, None, None


def _resolver_dia_semana(tipo: str, periodo: Optional[str], data_ref: date) -> Optional[str]:
    # Para GANHO semanal, nao ha um unico dia representativo.
    if tipo == "GANHO" and periodo == "SEMANAL":
        return None
    return _dia_semana_por_data(data_ref)


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


def criar_lancamento(db: Session, dados: LancamentoCriar, auto_commit: bool = True) -> Lancamento:
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

    periodo, minutos_corrida, km_corrida = _resolver_campos_ganho(dados, tipo)

    data_ref = dados.data_lancamento or date.today()
    dia_semana = _resolver_dia_semana(tipo, periodo, data_ref)

    moto_id = _resolver_moto_do_lancamento(db, dados.usuario_id, dados.moto_usuario_id)

    lancamento = Lancamento(
        usuario_id=dados.usuario_id,
        categoria_id=dados.categoria_id,
        moto_usuario_id=moto_id,
        tipo=tipo,
        valor=dados.valor,
        descricao=dados.descricao,
        dia_semana=dia_semana,
        periodo=periodo,
        minutos_corrida=minutos_corrida,
        km_corrida=km_corrida,
        data_lancamento=data_ref,
    )

    db.add(lancamento)
    if auto_commit:
        db.commit()
        db.refresh(lancamento)
    else:
        db.flush()

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


def atualizar_lancamento(
    db: Session,
    lancamento_id: int,
    dados: LancamentoCriar,
    auto_commit: bool = True,
) -> Lancamento:
    lancamento = db.execute(
        select(Lancamento).where(
            Lancamento.id == lancamento_id,
            Lancamento.usuario_id == dados.usuario_id,
        )
    ).scalar_one_or_none()
    if not lancamento:
        raise ValueError("lancamento_nao_encontrado")

    abastecimento = db.execute(
        select(Abastecimento).where(Abastecimento.lancamento_id == lancamento_id)
    ).scalar_one_or_none()
    manutencao = db.execute(
        select(Manutencao).where(Manutencao.lancamento_id == lancamento_id)
    ).scalar_one_or_none()

    tipo = dados.tipo.upper()
    if tipo not in ["GANHO", "DESPESA"]:
        raise ValueError("tipo_invalido")

    if abastecimento or manutencao:
        if tipo != "DESPESA":
            raise ValueError("lancamento_vinculado_apenas_despesa")

    categoria = db.execute(
        select(Categoria).where(Categoria.id == dados.categoria_id)
    ).scalar_one_or_none()
    if not categoria:
        raise ValueError("categoria_nao_encontrada")
    if not categoria.ativo:
        raise ValueError("categoria_inativa")
    if tipo != categoria.tipo:
        raise ValueError("tipo_incompativel_com_categoria")

    if abastecimento or manutencao:
        if categoria.tipo != "DESPESA":
            raise ValueError("lancamento_vinculado_apenas_despesa")

    periodo, minutos_corrida, km_corrida = _resolver_campos_ganho(dados, tipo)

    data_ref = dados.data_lancamento or date.today()
    dia_semana = _resolver_dia_semana(tipo, periodo, data_ref)

    moto_id = _resolver_moto_do_lancamento(db, dados.usuario_id, dados.moto_usuario_id)

    lancamento.categoria_id = dados.categoria_id
    lancamento.moto_usuario_id = moto_id
    lancamento.tipo = tipo
    lancamento.valor = dados.valor
    lancamento.descricao = dados.descricao
    lancamento.dia_semana = dia_semana
    lancamento.periodo = periodo
    lancamento.minutos_corrida = minutos_corrida
    lancamento.km_corrida = km_corrida
    lancamento.data_lancamento = data_ref

    if abastecimento:
        abastecimento.usuario_id = dados.usuario_id
        abastecimento.moto_usuario_id = moto_id
        abastecimento.valor_total = dados.valor
        abastecimento.valor_litro = dados.valor / Decimal(abastecimento.litros)
        abastecimento.data_abastecimento = lancamento.data_lancamento

    if manutencao:
        manutencao.usuario_id = dados.usuario_id
        manutencao.moto_usuario_id = moto_id
        manutencao.valor_total = dados.valor
        manutencao.data_manutencao = lancamento.data_lancamento

    if auto_commit:
        db.commit()
        db.refresh(lancamento)
    else:
        db.flush()
    return lancamento


def excluir_lancamento(db: Session, lancamento_id: int, usuario_id: int, auto_commit: bool = True) -> None:
    lancamento = db.execute(
        select(Lancamento).where(
            Lancamento.id == lancamento_id,
            Lancamento.usuario_id == usuario_id,
        )
    ).scalar_one_or_none()
    if not lancamento:
        raise ValueError("lancamento_nao_encontrado")

    db.delete(lancamento)
    if auto_commit:
        db.commit()
    else:
        db.flush()
