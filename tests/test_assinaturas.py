from unittest.mock import MagicMock, patch
import pytest

from app.core.config import settings


async def _criar_usuario_logado(client, email: str = "assinatura@test.com") -> dict[str, str]:
    resposta_usuario = await client.post(
        "/usuarios",
        json={"nome": "Usuario Assinatura", "email": email, "senha": "senha123"},
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
async def test_obter_precos_assinatura(client):
    resposta = await client.get("/assinaturas/precos")
    assert resposta.status_code == 200
    data = resposta.json()
    assert "mensal" in data
    assert "anual" in data
    assert "stripe_publishable_key" in data


@pytest.mark.anyio
async def test_obter_status_assinatura_usuario_free(client):
    headers = await _criar_usuario_logado(client, email="status_free@test.com")
    resposta = await client.get("/assinaturas/status", headers=headers)
    assert resposta.status_code == 200
    data = resposta.json()
    assert data["plano"] == "FREE"
    assert data["em_trial"] is True
    assert data["dias_trial_restantes"] <= 7


@pytest.mark.anyio
async def test_criar_checkout_session_embedded_com_sucesso(client):
    headers = await _criar_usuario_logado(client, email="checkout_success@test.com")

    # Garante que temos um price_id válido nas settings de teste
    settings.stripe_price_mensal = "price_mensal_test_123"

    mock_customer = MagicMock()
    mock_customer.id = "cus_test_123"

    mock_session = MagicMock()
    mock_session.client_secret = "cs_test_secret_123456"
    mock_session.url = "http://testserver/embedded"

    with patch("stripe.Customer.create", return_value=mock_customer), \
         patch("stripe.checkout.Session.create", return_value=mock_session):
        resposta = await client.post(
            "/assinaturas/checkout",
            headers=headers,
            json={"price_id": "price_mensal_test_123"},
        )

        assert resposta.status_code == 200
        data = resposta.json()
        assert data["client_secret"] == "cs_test_secret_123456"


@pytest.mark.anyio
async def test_criar_checkout_origem_dinamica_mobile(client):
    headers = await _criar_usuario_logado(client, email="checkout_mobile@test.com")
    headers["Origin"] = "https://minha-aplicacao.trycloudflare.com"

    settings.stripe_price_mensal = "price_mensal_test_123"
    settings.stripe_payment_method_configuration = "pmc_test_123"

    mock_customer = MagicMock()
    mock_customer.id = "cus_test_mobile"

    mock_session = MagicMock()
    mock_session.client_secret = "cs_test_secret_mobile"
    mock_session.url = "https://minha-aplicacao.trycloudflare.com/embedded"

    with patch("stripe.Customer.create", return_value=mock_customer), \
         patch("stripe.checkout.Session.create", return_value=mock_session) as mock_create_session:
        resposta = await client.post(
            "/assinaturas/checkout",
            headers=headers,
            json={"price_id": "price_mensal_test_123"},
        )

        assert resposta.status_code == 200
        call_kwargs = mock_create_session.call_args.kwargs
        assert "https://minha-aplicacao.trycloudflare.com/configuracoes" in call_kwargs["return_url"]
        assert call_kwargs["payment_method_configuration"] == "pmc_test_123"


@pytest.mark.anyio
async def test_criar_checkout_preco_invalido_retorna_400(client):
    headers = await _criar_usuario_logado(client, email="checkout_invalid@test.com")
    resposta = await client.post(
        "/assinaturas/checkout",
        headers=headers,
        json={"price_id": "price_invalido_xyz"},
    )
    assert resposta.status_code == 400
    assert "Plano invalido" in resposta.json()["detail"]


@pytest.mark.anyio
async def test_cancelar_assinatura_sem_subscription_ativa_retorna_400(client):
    headers = await _criar_usuario_logado(client, email="cancel_no_sub@test.com")
    resposta = await client.post("/assinaturas/cancelar", headers=headers)
    assert resposta.status_code == 400
    assert "Nenhuma assinatura ativa" in resposta.json()["detail"]


@pytest.mark.anyio
async def test_cancelar_assinatura_com_sucesso(client, db_session):
    headers = await _criar_usuario_logado(client, email="cancel_success@test.com")

    # Simular assinatura ativa no usuário
    from app.models.usuario import Usuario
    user = db_session.query(Usuario).filter_by(email="cancel_success@test.com").first()
    user.stripe_subscription_id = "sub_test_999"
    user.plano = "PRO"
    db_session.commit()

    with patch("stripe.Subscription.modify") as mock_modify:
        resposta = await client.post("/assinaturas/cancelar", headers=headers)
        assert resposta.status_code == 200
        assert "Assinatura sera cancelada" in resposta.json()["mensagem"]
        mock_modify.assert_called_once_with("sub_test_999", cancel_at_period_end=True)


@pytest.mark.anyio
async def test_criar_checkout_infinitepay(client):
    headers = await _criar_usuario_logado(client, email="infinitepay_checkout@test.com")
    resposta = await client.post(
        "/assinaturas/checkout/infinitepay",
        headers=headers,
        json={"plano": "pix_avulso"},
    )
    assert resposta.status_code == 200
    data = resposta.json()
    assert "checkout_url" in data
    assert "order_nsu" in data


@pytest.mark.anyio
async def test_webhook_infinitepay_ativa_plano_pro(client, db_session):
    headers = await _criar_usuario_logado(client, email="webhook_infpay@test.com")
    from app.models.usuario import Usuario
    user = db_session.query(Usuario).filter_by(email="webhook_infpay@test.com").first()
    assert user.plano == "FREE"

    order_nsu = f"user_{user.id}_12345678"
    payload = {
        "invoice_slug": "inv_test_123",
        "amount": 990,
        "paid_amount": 990,
        "capture_method": "pix",
        "transaction_nsu": "tx_test_999",
        "order_nsu": order_nsu,
    }

    resposta = await client.post("/assinaturas/webhook/infinitepay", json=payload)
    assert resposta.status_code == 200
    assert resposta.json() == {"success": True, "message": None}

    db_session.refresh(user)
    assert user.plano == "PRO"
    assert user.plano_expira_em is not None


@pytest.mark.anyio
async def test_gerar_pix_direto(client):
    headers = await _criar_usuario_logado(client, email="pix_direto@test.com")
    resposta = await client.post(
        "/assinaturas/pix/gerar",
        headers=headers,
        json={"plano": "pix_avulso"},
    )
    assert resposta.status_code == 200
    data = resposta.json()
    assert "qr_code_text" in data
    assert "qr_code_url" in data
    assert "order_nsu" in data
    assert data["valor_formatado"] == "R$ 9,99"


@pytest.mark.anyio
async def test_checar_pix_status(client, db_session):
    headers = await _criar_usuario_logado(client, email="pix_check@test.com")
    from app.models.usuario import Usuario
    user = db_session.query(Usuario).filter_by(email="pix_check@test.com").first()

    # Primeiro checagem em conta FREE
    resp1 = await client.post(
        "/assinaturas/pix/checar",
        headers=headers,
        json={"order_nsu": f"user_{user.id}_9999"},
    )
    assert resp1.status_code == 200
    assert resp1.json()["pago"] is False

    # Simular ativação PRO
    user.plano = "PRO"
    db_session.commit()

    resp2 = await client.post(
        "/assinaturas/pix/checar",
        headers=headers,
        json={"order_nsu": f"user_{user.id}_9999"},
    )
    assert resp2.status_code == 200
    assert resp2.json()["pago"] is True
    assert resp2.json()["plano"] == "PRO"


