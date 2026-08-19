from datetime import date

import pytest


async def _criar_usuario_logado(client, email: str = "api@test.com") -> dict[str, str]:
    resposta_usuario = await client.post(
        "/usuarios",
        json={"nome": "Usuario API", "email": email, "senha": "senha123"},
    )
    assert resposta_usuario.status_code == 201

    resposta_login = await client.post(
        "/auth/login",
        json={"email": email, "senha": "senha123"},
    )
    assert resposta_login.status_code == 200

    token = resposta_login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.anyio
async def test_auth_endpoints_criam_usuario_login_e_me(client):
    headers = await _criar_usuario_logado(client)

    resposta = await client.get("/auth/me", headers=headers)

    assert resposta.status_code == 200
    assert resposta.json()["email"] == "api@test.com"


@pytest.mark.anyio
async def test_refresh_token_gera_novos_tokens(client):
    await client.post(
        "/usuarios",
        json={"nome": "Usuario Refresh", "email": "refresh@test.com", "senha": "senha123"},
    )
    res_login = await client.post(
        "/auth/login",
        json={"email": "refresh@test.com", "senha": "senha123"},
    )
    assert res_login.status_code == 200
    body = res_login.json()
    assert "access_token" in body
    assert "refresh_token" in body

    refresh_token = body["refresh_token"]

    res_refresh = await client.post(
        "/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert res_refresh.status_code == 200
    body_refreshed = res_refresh.json()
    assert "access_token" in body_refreshed
    assert "refresh_token" in body_refreshed

    # Verifica se o novo access token funciona em rota protegida
    headers = {"Authorization": f"Bearer {body_refreshed['access_token']}"}
    res_me = await client.get("/auth/me", headers=headers)
    assert res_me.status_code == 200
    assert res_me.json()["email"] == "refresh@test.com"


@pytest.mark.anyio
async def test_consulta_placa_invalida_retorna_422_e_preserva_token(client):
    headers = await _criar_usuario_logado(client)

    resposta = await client.get("/motos/consulta-placa/ABC", headers=headers)

    assert resposta.status_code == 422
    assert "Placa Invalida" in resposta.json()["detail"]

    resposta_me = await client.get("/auth/me", headers=headers)
    assert resposta_me.status_code == 200


@pytest.mark.anyio
async def test_fluxo_http_moto_categoria_lancamento(client):
    headers = await _criar_usuario_logado(client)

    resposta_moto = await client.post(
        "/motos/minha",
        headers=headers,
        json={
            "marca_manual": "HONDA",
            "modelo_manual": "CG 160",
            "ano_manual": 2024,
            "km_atual": 1200,
            "cor": "Preta",
        },
    )
    assert resposta_moto.status_code == 201
    moto_id = resposta_moto.json()["id"]

    resposta_categoria = await client.post(
        "/categorias",
        headers=headers,
        json={"nome": "Corridas API", "tipo": "GANHO"},
    )
    assert resposta_categoria.status_code == 201
    categoria_id = resposta_categoria.json()["id"]

    resposta_lancamento = await client.post(
        "/lancamentos",
        headers=headers,
        json={
            "categoria_id": categoria_id,
            "tipo": "GANHO",
            "valor": "150.00",
            "descricao": "Dia de trabalho",
            "periodo": "DIARIO",
            "data_lancamento": date.today().isoformat(),
            "moto_usuario_id": moto_id,
        },
    )
    assert resposta_lancamento.status_code == 201
    assert resposta_lancamento.json()["valor"] == "150.00"

    resposta_lista = await client.get("/lancamentos", headers=headers)
    assert resposta_lista.status_code == 200
    assert resposta_lista.json()["total"] == 1
