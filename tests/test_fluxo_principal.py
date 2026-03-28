from decimal import Decimal

import pytest

from app.core.security import gerar_token_acesso, validar_token_acesso
from app.schemas.categoria import CategoriaCriar
from app.schemas.lancamento import LancamentoCriar
from app.schemas.manutencao import ManutencaoCriar
from app.schemas.moto import MotoUsuarioCriarPorPlaca
from app.schemas.usuario import UsuarioCriar
from app.services import moto_service
from app.services.categoria_service import criar_categoria
from app.services.lancamento_service import criar_lancamento
from app.services.manutencao_service import criar_manutencao
from app.services.usuario_service import autenticar_usuario, criar_usuario


def test_auth_servicos_token(db_session):
    usuario = criar_usuario(
        db_session,
        UsuarioCriar(
            nome="Teste Usuario",
            email="me@test.com",
            senha="senha123",
        ),
    )

    autenticado = autenticar_usuario(db_session, "me@test.com", "senha123")
    assert autenticado.id == usuario.id

    token = gerar_token_acesso(usuario.id, usuario.email)
    payload = validar_token_acesso(token)
    assert int(payload["sub"]) == usuario.id
    assert payload["email"] == usuario.email

    with pytest.raises(ValueError):
        autenticar_usuario(db_session, "me@test.com", "senha-errada")


def test_fluxo_moto_por_placa_cache_lancamento_e_manutencao(db_session, monkeypatch):
    chamadas = {"wdapi": 0}

    def fake_consulta_placa(_placa: str):
        chamadas["wdapi"] += 1
        return {
            "placa_consultada": "TTY4G26",
            "extra_disponivel": False,
            "fipe_disponivel": False,
            "fipe_melhor_correspondencia": None,
            "dados": {
                "ano": "2025",
                "anoModelo": "2026",
                "cor": "VERMELHA",
                "extra": {},
                "fipe": {},
                "marca": "HONDA",
                "modelo": "CG 160 START",
                "municipio": "Belford Roxo",
                "origem": "NACIONAL",
                "placa": "TTY4G26",
                "situacao": "Sem restrição",
                "uf": "RJ",
            },
        }

    monkeypatch.setattr(moto_service, "consultar_dados_veiculo_por_placa", fake_consulta_placa)

    usuario = criar_usuario(
        db_session,
        UsuarioCriar(
            nome="Fluxo Usuario",
            email="fluxo@test.com",
            senha="senha123",
        ),
    )

    moto = moto_service.criar_moto_usuario_por_placa(
        db_session,
        usuario.id,
        MotoUsuarioCriarPorPlaca(
            placa="TTY4G26",
            km_atual=1000,
        ),
    )
    assert moto.origem_dados == "WDAPI"
    assert moto.placa == "TTY4G26"
    assert chamadas["wdapi"] == 1

    consulta_cache = moto_service.consultar_dados_veiculo_por_placa_com_cache(db_session, "TTY4G26")
    assert consulta_cache["placa_consultada"] == "TTY4G26"
    assert chamadas["wdapi"] == 1

    categoria = criar_categoria(
        db_session,
        CategoriaCriar(
            nome="Combustivel",
            tipo="DESPESA",
        ),
    )

    lancamento = criar_lancamento(
        db_session,
        LancamentoCriar(
            usuario_id=usuario.id,
            categoria_id=categoria.id,
            tipo="DESPESA",
            valor=Decimal("20.00"),
            descricao="Teste lancamento",
        ),
    )
    assert lancamento.usuario_id == usuario.id
    assert lancamento.moto_usuario_id == moto.id

    manutencao = criar_manutencao(
        db_session,
        ManutencaoCriar(
            usuario_id=usuario.id,
            categoria_id=categoria.id,
            valor_total=Decimal("35.00"),
            descricao_servico="Troca de filtro",
        ),
    )
    assert manutencao.usuario_id == usuario.id
    assert manutencao.lancamento_id is not None
