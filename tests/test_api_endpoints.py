from datetime import date

# pyrefly: ignore [missing-import]
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


@pytest.mark.anyio
async def test_atualizar_km_rapido_moto_com_e_sem_troca_oleo(client):
    auth_headers = await _criar_usuario_logado(client)

    # 1. Cadastra uma moto
    resp_moto = await client.post(
        "/motos/minha",
        headers=auth_headers,
        json={
            "marca_manual": "Honda",
            "modelo_manual": "CG 160 Fan",
            "ano_manual": 2022,
            "km_atual": 10000,
            "cor": "Preta",
        },
    )
    assert resp_moto.status_code == 201
    assert resp_moto.json()["km_atual"] == 10000

    # 2. Atualiza apenas o KM (sem troca de oleo)
    resp_km1 = await client.patch(
        "/motos/minha/km",
        headers=auth_headers,
        json={"km_atual": 10500, "trocou_oleo": False},
    )
    assert resp_km1.status_code == 200
    assert resp_km1.json()["km_atual"] == 10500

    # 3. Atualiza o KM com Troca de Oleo (cria despesa de manutencao)
    resp_km2 = await client.patch(
        "/motos/minha/km",
        headers=auth_headers,
        json={
            "km_atual": 11000,
            "trocou_oleo": True,
            "valor_oleo": "45.00",
            "oficina": "Oficina Central",
        },
    )
    assert resp_km2.status_code == 200
    assert resp_km2.json()["km_atual"] == 11000

    # 4. Verifica se a manutencao foi registrada
    resp_manu = await client.get("/manutencoes", headers=auth_headers)
    assert resp_manu.status_code == 200
    assert len(resp_manu.json()) == 1
    assert resp_manu.json()[0]["valor_total"] == "45.00"
    assert resp_manu.json()[0]["tipo_servico"] == "TROCA_OLEO"


@pytest.mark.anyio
async def test_busca_e_exclusao_em_lote_lancamentos(client):
    headers = await _criar_usuario_logado(client, "busca_lote@test.com")

    # Cadastra moto obrigatoria
    await client.post(
        "/motos/minha",
        headers=headers,
        json={"marca_manual": "Honda", "modelo_manual": "CG 160", "ano_manual": 2022, "km_atual": 5000},
    )

    # Cadastra categoria de despesa
    res_cat = await client.post(
        "/categorias",
        headers=headers,
        json={"nome": "Manutenção Geral", "tipo": "DESPESA", "grupo_despesa": "GERAL"},
    )
    assert res_cat.status_code == 201
    cat_id = res_cat.json()["id"]

    # Cria 3 lançamentos
    res1 = await client.post(
        "/lancamentos",
        headers=headers,
        json={"categoria_id": cat_id, "tipo": "DESPESA", "valor": "50.00", "descricao": "Troca de pneu traseiro", "data_lancamento": "2026-08-20"},
    )
    res2 = await client.post(
        "/lancamentos",
        headers=headers,
        json={"categoria_id": cat_id, "tipo": "DESPESA", "valor": "30.00", "descricao": "Lâmpada do farol", "data_lancamento": "2026-08-21"},
    )
    res3 = await client.post(
        "/lancamentos",
        headers=headers,
        json={"categoria_id": cat_id, "tipo": "DESPESA", "valor": "20.00", "descricao": "Troca de pneu dianteiro", "data_lancamento": "2026-08-22"},
    )

    id1 = res1.json()["id"]
    id2 = res2.json()["id"]
    id3 = res3.json()["id"]

    # Teste de busca por texto livre na descricao: "pneu"
    res_busca = await client.get("/lancamentos", headers=headers, params={"busca": "pneu"})
    assert res_busca.status_code == 200
    itens_busca = res_busca.json()["itens"]
    assert len(itens_busca) == 2
    assert {i["id"] for i in itens_busca} == {id1, id3}

    # Teste de exclusão em lote (deleta id1 e id2)
    res_lote = await client.request("DELETE", "/lancamentos/lote", headers=headers, json={"ids": [id1, id2]})
    assert res_lote.status_code == 200
    assert res_lote.json()["quantidade"] == 2

    # Verifica se restar apenas id3
    res_final = await client.get("/lancamentos", headers=headers)
    assert res_final.status_code == 200
    itens_finais = res_final.json()["itens"]
    assert len(itens_finais) == 1
    assert itens_finais[0]["id"] == id3

