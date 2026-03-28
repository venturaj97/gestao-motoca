from datetime import date
from decimal import Decimal

import pytest

from app.schemas.categoria import CategoriaCriar
from app.schemas.lancamento import LancamentoCriar
from app.schemas.meta import MetaCriar
from app.schemas.moto import MotoUsuarioCriar
from app.schemas.usuario import UsuarioCriar
from app.services.categoria_service import criar_categoria
from app.services.lancamento_service import criar_lancamento
from app.services.meta_service import criar_meta, listar_alertas_metas
from app.services.moto_service import criar_moto_usuario
from app.services.usuario_service import criar_usuario
from app.services.visao_mes_service import obter_visao_mes


def _criar_contexto_base(db_session):
    usuario = criar_usuario(
        db_session,
        UsuarioCriar(nome="Usuario Meta", email="meta@test.com", senha="senha123"),
    )
    criar_moto_usuario(
        db_session,
        MotoUsuarioCriar(
            usuario_id=usuario.id,
            marca_manual="HONDA",
            modelo_manual="CG",
            ano_manual=2024,
            km_atual=1000,
            cor="Preta",
        ),
    )

    categoria_ganho = criar_categoria(db_session, CategoriaCriar(nome="Corridas", tipo="GANHO"))
    categoria_despesa = criar_categoria(db_session, CategoriaCriar(nome="Combustivel", tipo="DESPESA"))
    return usuario, categoria_ganho, categoria_despesa


def test_alerta_meta_ganho_atingida(db_session):
    usuario, categoria_ganho, _ = _criar_contexto_base(db_session)
    hoje = date.today()

    criar_meta(
        db_session,
        usuario.id,
        MetaCriar(
            nome="Meta ganho mensal",
            tipo="GANHO",
            periodo="MENSAL",
            valor_meta=Decimal("1000.00"),
        ),
    )

    criar_lancamento(
        db_session,
        LancamentoCriar(
            usuario_id=usuario.id,
            categoria_id=categoria_ganho.id,
            tipo="GANHO",
            valor=Decimal("1200.00"),
            periodo="DIARIO",
            data_lancamento=hoje,
        ),
    )

    alertas = listar_alertas_metas(db_session, usuario.id, data_ref=hoje)
    assert len(alertas) == 1
    assert alertas[0]["status"] == "atingida"
    assert alertas[0]["tipo"] == "GANHO"


def test_alerta_meta_despesa_estourada(db_session):
    usuario, _, categoria_despesa = _criar_contexto_base(db_session)
    hoje = date.today()

    criar_meta(
        db_session,
        usuario.id,
        MetaCriar(
            nome="Limite despesas mensal",
            tipo="DESPESA",
            periodo="MENSAL",
            valor_meta=Decimal("300.00"),
        ),
    )

    criar_lancamento(
        db_session,
        LancamentoCriar(
            usuario_id=usuario.id,
            categoria_id=categoria_despesa.id,
            tipo="DESPESA",
            valor=Decimal("350.00"),
            data_lancamento=hoje,
        ),
    )

    alertas = listar_alertas_metas(db_session, usuario.id, data_ref=hoje)
    assert len(alertas) == 1
    assert alertas[0]["status"] == "estourada"
    assert alertas[0]["tipo"] == "DESPESA"


def test_visao_mes_consolidada(db_session):
    usuario, categoria_ganho, categoria_despesa = _criar_contexto_base(db_session)
    hoje = date.today()

    criar_meta(
        db_session,
        usuario.id,
        MetaCriar(
            nome="Meta ganho mensal",
            tipo="GANHO",
            periodo="MENSAL",
            valor_meta=Decimal("2000.00"),
        ),
    )
    criar_meta(
        db_session,
        usuario.id,
        MetaCriar(
            nome="Limite despesa mensal",
            tipo="DESPESA",
            periodo="MENSAL",
            valor_meta=Decimal("700.00"),
        ),
    )

    criar_lancamento(
        db_session,
        LancamentoCriar(
            usuario_id=usuario.id,
            categoria_id=categoria_ganho.id,
            tipo="GANHO",
            valor=Decimal("900.00"),
            periodo="DIARIO",
            data_lancamento=hoje,
        ),
    )
    criar_lancamento(
        db_session,
        LancamentoCriar(
            usuario_id=usuario.id,
            categoria_id=categoria_despesa.id,
            tipo="DESPESA",
            valor=Decimal("300.00"),
            data_lancamento=hoje,
        ),
    )

    visao = obter_visao_mes(
        db_session,
        usuario_id=usuario.id,
        ano=hoje.year,
        mes=hoje.month,
    )

    assert visao["ganho"]["total_periodo"] == Decimal("900.00")
    assert visao["despesa"]["total_periodo"] == Decimal("300.00")
    assert visao["saldo_mes"] == Decimal("600.00")
    assert len(visao["metas_ativas"]) == 2
    assert len(visao["alertas_mensais"]) == 2
    assert len(visao["resumo_executivo"]) > 0


def test_criar_meta_tipo_invalido(db_session):
    usuario, _, _ = _criar_contexto_base(db_session)

    with pytest.raises(ValueError):
        criar_meta(
            db_session,
            usuario.id,
            MetaCriar(
                nome="Meta invalida",
                tipo="OUTRO",
                periodo="MENSAL",
                valor_meta=Decimal("100.00"),
            ),
        )
