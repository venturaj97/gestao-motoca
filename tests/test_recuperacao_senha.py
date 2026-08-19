import pytest
from sqlalchemy import select
from app.models.recuperacao_senha import RecuperacaoSenha


@pytest.mark.anyio
async def test_fluxo_recuperacao_e_alteracao_de_senha(client, db_session):
    # 1. Cadastra usuário
    email = "recuperar@test.com"
    resp_cad = await client.post(
        "/usuarios",
        json={"nome": "Entregador Teste", "email": email, "senha": "senhaAntiga123"},
    )
    assert resp_cad.status_code == 201

    # 2. Solicita recuperação de senha
    resp_solicitar = await client.post(
        "/auth/solicitar-recuperacao",
        json={"email": email},
    )
    assert resp_solicitar.status_code == 200

    # Busca o PIN gerado no banco de testes
    rec = db_session.execute(
        select(RecuperacaoSenha).where(RecuperacaoSenha.usado == False)  # noqa: E712
    ).scalar_one_or_none()
    assert rec is not None
    assert len(rec.codigo_pin) == 6

    # 3. Tenta redefinir com PIN incorreto
    resp_erro_pin = await client.post(
        "/auth/redefinir-senha",
        json={"email": email, "codigo_pin": "000000", "nova_senha": "senhaNova123"},
    )
    assert resp_erro_pin.status_code == 400

    # 4. Redefine a senha com o PIN correto
    resp_redefinir = await client.post(
        "/auth/redefinir-senha",
        json={"email": email, "codigo_pin": rec.codigo_pin, "nova_senha": "senhaNova123"},
    )
    assert resp_redefinir.status_code == 200

    # 5. Tenta login com a nova senha
    resp_login_novo = await client.post(
        "/auth/login",
        json={"email": email, "senha": "senhaNova123"},
    )
    assert resp_login_novo.status_code == 200
    token = resp_login_novo.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 6. Altera a senha estando logado
    resp_alterar = await client.put(
        "/auth/alterar-senha",
        json={"senha_atual": "senhaNova123", "nova_senha": "senhaSuperNova456"},
        headers=headers,
    )
    assert resp_alterar.status_code == 200

    # 7. Confirma login com a senha alterada
    resp_login_final = await client.post(
        "/auth/login",
        json={"email": email, "senha": "senhaSuperNova456"},
    )
    assert resp_login_final.status_code == 200
