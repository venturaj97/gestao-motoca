# # pyrefly: ignore [missing-import]
# import pytest
# # pyrefly: ignore [missing-import]
# from sqlalchemy import select
# from app.models.recuperacao_senha import RecuperacaoSenha


# @pytest.mark.anyio
# async def test_fluxo_recuperacao_e_alteracao_de_senha(client, db_session):
#     # 1. Cadastra usuário
#     email = "recuperar@test.com"
#     resp_cad = await client.post(
#         "/usuarios",
#         json={"nome": "Entregador Teste", "email": email, "senha": "senhaAntiga123"},
#     )
#     assert resp_cad.status_code == 201

#     # 2. Solicita recuperação de senha
#     resp_solicitar = await client.post(
#         "/auth/solicitar-recuperacao",
#         json={"email": email},
#     )
#     assert resp_solicitar.status_code == 200

#     # Busca o PIN gerado no banco de testes
#     rec = db_session.execute(
#         select(RecuperacaoSenha).where(RecuperacaoSenha.usado == False)  # noqa: E712
#     ).scalar_one_or_none()
#     assert rec is not None
#     assert len(rec.codigo_pin) == 6

#     # 3. Tenta redefinir com PIN incorreto
#     resp_erro_pin = await client.post(
#         "/auth/redefinir-senha",
#         json={"email": email, "codigo_pin": "000000", "nova_senha": "senhaNova123"},
#     )
#     assert resp_erro_pin.status_code == 400

#     # 4. Redefine a senha com o PIN correto
#     resp_redefinir = await client.post(
#         "/auth/redefinir-senha",
#         json={"email": email, "codigo_pin": rec.codigo_pin, "nova_senha": "senhaNova123"},
#     )
#     assert resp_redefinir.status_code == 200

#     # 5. Tenta login com a nova senha
#     resp_login_novo = await client.post(
#         "/auth/login",
#         json={"email": email, "senha": "senhaNova123"},
#     )
#     assert resp_login_novo.status_code == 200
#     token = resp_login_novo.json()["access_token"]
#     headers = {"Authorization": f"Bearer {token}"}

#     # 5.1 Confirma se o e-mail foi marcado como confirmado automaticamente
#     resp_me = await client.get("/auth/me", headers=headers)
#     assert resp_me.status_code == 200
#     assert resp_me.json()["email_confirmado"] is True

#     # 6. Altera a senha estando logado
#     resp_alterar = await client.put(
#         "/auth/alterar-senha",
#         json={"senha_atual": "senhaNova123", "nova_senha": "senhaSuperNova456"},
#         headers=headers,
#     )
#     assert resp_alterar.status_code == 200

#     # 7. Confirma login com a senha alterada
#     resp_login_final = await client.post(
#         "/auth/login",
#         json={"email": email, "senha": "senhaSuperNova456"},
#     )
#     assert resp_login_final.status_code == 200


# @pytest.mark.anyio
# async def test_fluxo_confirmacao_de_email(client, db_session):
#     email = "confirmaremail@test.com"
#     await client.post(
#         "/usuarios",
#         json={"nome": "Entregador Confirmar", "email": email, "senha": "senhaValida123"},
#     )
#     res_login = await client.post(
#         "/auth/login",
#         json={"email": email, "senha": "senhaValida123"},
#     )
#     token = res_login.json()["access_token"]
#     headers = {"Authorization": f"Bearer {token}"}

#     # Verifica se inicia com email_confirmado == False
#     res_me = await client.get("/auth/me", headers=headers)
#     assert res_me.status_code == 200
#     assert res_me.json()["email_confirmado"] is False

#     # Solicita envio do código de confirmação
#     res_envio = await client.post("/auth/enviar-confirmacao-email", headers=headers)
#     assert res_envio.status_code == 200

#     # Busca PIN no banco
#     rec = db_session.execute(
#         select(RecuperacaoSenha).where(RecuperacaoSenha.usado == False)  # noqa: E712
#     ).scalar_one_or_none()
#     assert rec is not None

#     # Confirma o e-mail enviando o PIN
#     res_confirm = await client.post(
#         "/auth/confirmar-email",
#         json={"codigo_pin": rec.codigo_pin},
#         headers=headers,
#     )
#     assert res_confirm.status_code == 200

#     # Verifica se agora email_confirmado == True
#     res_me_depois = await client.get("/auth/me", headers=headers)
#     assert res_me_depois.status_code == 200
#     assert res_me_depois.json()["email_confirmado"] is True
