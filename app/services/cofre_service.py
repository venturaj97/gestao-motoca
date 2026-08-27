from decimal import Decimal
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.cofre import Cofre
from app.schemas.cofre import CofreCriar, CofreAtualizar, CofreAporte


def _montar_resposta_cofre(cofre: Cofre) -> dict:
    valor_meta = Decimal(cofre.valor_meta)
    saldo_atual = Decimal(cofre.saldo_atual)
    valor_restante = max(Decimal("0.00"), valor_meta - saldo_atual)
    percentual = min(Decimal("100.00"), (saldo_atual / valor_meta) * Decimal("100.00")) if valor_meta > 0 else Decimal("0.00")

    return {
        "id": cofre.id,
        "usuario_id": cofre.usuario_id,
        "nome": cofre.nome,
        "categoria": cofre.categoria,
        "valor_meta": valor_meta,
        "saldo_atual": saldo_atual,
        "porcentagem_autoguarda": Decimal(cofre.porcentagem_autoguarda),
        "ativa": cofre.ativa,
        "valor_restante": valor_restante,
        "percentual_meta": round(percentual, 2),
        "data_criacao": cofre.data_criacao,
    }


def listar_cofres(db: Session, usuario_id: int) -> list[dict]:
    cofres = db.execute(
        select(Cofre).where(
            Cofre.usuario_id == usuario_id,
            Cofre.situacao == "ATIVO",
        ).order_by(Cofre.id.desc())
    ).scalars().all()

    return [_montar_resposta_cofre(c) for c in cofres]


def obter_cofre_por_id(db: Session, cofre_id: int, usuario_id: int) -> Cofre:
    cofre = db.execute(
        select(Cofre).where(
            Cofre.id == cofre_id,
            Cofre.usuario_id == usuario_id,
            Cofre.situacao == "ATIVO",
        )
    ).scalar_one_or_none()
    if not cofre:
        raise ValueError("cofre_nao_encontrado")
    return cofre


def criar_cofre(db: Session, usuario_id: int, dados: CofreCriar) -> dict:
    cofre = Cofre(
        usuario_id=usuario_id,
        nome=dados.nome.strip(),
        categoria=dados.categoria.upper().strip(),
        valor_meta=dados.valor_meta,
        saldo_atual=dados.saldo_atual or Decimal("0.00"),
        porcentagem_autoguarda=dados.porcentagem_autoguarda or Decimal("0.00"),
        ativa=dados.ativa,
    )
    db.add(cofre)
    db.commit()
    db.refresh(cofre)
    return _montar_resposta_cofre(cofre)


def atualizar_cofre(db: Session, cofre_id: int, usuario_id: int, dados: CofreAtualizar) -> dict:
    cofre = obter_cofre_por_id(db, cofre_id, usuario_id)

    if dados.nome is not None:
        cofre.nome = dados.nome.strip()
    if dados.categoria is not None:
        cofre.categoria = dados.categoria.upper().strip()
    if dados.valor_meta is not None:
        cofre.valor_meta = dados.valor_meta
    if dados.saldo_atual is not None:
        cofre.saldo_atual = dados.saldo_atual
    if dados.porcentagem_autoguarda is not None:
        cofre.porcentagem_autoguarda = dados.porcentagem_autoguarda
    if dados.ativa is not None:
        cofre.ativa = dados.ativa

    db.commit()
    db.refresh(cofre)
    return _montar_resposta_cofre(cofre)


def aportar_saldo_cofre(db: Session, cofre_id: int, usuario_id: int, dados: CofreAporte) -> dict:
    cofre = obter_cofre_por_id(db, cofre_id, usuario_id)
    tipo = dados.tipo_operacao.upper().strip()
    valor = Decimal(dados.valor)

    if tipo == "DEPOSITO":
        cofre.saldo_atual = Decimal(cofre.saldo_atual) + valor
    elif tipo == "SAQUE":
        if Decimal(cofre.saldo_atual) < valor:
            raise ValueError("saldo_insuficiente")
        cofre.saldo_atual = Decimal(cofre.saldo_atual) - valor
    else:
        raise ValueError("tipo_operacao_invalido")

    db.commit()
    db.refresh(cofre)
    return _montar_resposta_cofre(cofre)


def excluir_cofre(db: Session, cofre_id: int, usuario_id: int) -> None:
    cofre = obter_cofre_por_id(db, cofre_id, usuario_id)
    cofre.situacao = "EXCLUIDO"
    cofre.ativa = False
    db.commit()


def processar_autoguarda_cofres(db: Session, usuario_id: int, valor_ganho: Decimal) -> None:
    """
    Sempre que um lançamento de GANHO for criado, calcula e credita a porcentagem
    em todos os cofres ativos do usuário que possuam porcentagem_autoguarda > 0.
    """
    if valor_ganho <= 0:
        return

    cofres_autoguarda = db.execute(
        select(Cofre).where(
            Cofre.usuario_id == usuario_id,
            Cofre.ativa == True,  # noqa: E712
            Cofre.situacao == "ATIVO",
            Cofre.porcentagem_autoguarda > 0,
        )
    ).scalars().all()

    for cofre in cofres_autoguarda:
        pct = Decimal(cofre.porcentagem_autoguarda) / Decimal("100.00")
        valor_creditar = valor_ganho * pct
        cofre.saldo_atual = Decimal(cofre.saldo_atual) + valor_creditar
