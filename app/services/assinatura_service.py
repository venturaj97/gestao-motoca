"""Serviço de integração com Stripe para assinaturas PRO."""

from datetime import datetime, timezone

import stripe
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.usuario import Usuario

stripe.api_key = settings.stripe_secret_key


def _obter_ou_criar_customer(db: Session, usuario: Usuario) -> str:
    """Retorna o stripe_customer_id do usuario, criando se necessario."""
    if usuario.stripe_customer_id:
        return usuario.stripe_customer_id

    customer = stripe.Customer.create(
        email=usuario.email,
        name=usuario.nome,
        metadata={"usuario_id": str(usuario.id)},
    )

    usuario.stripe_customer_id = customer.id
    db.commit()
    return customer.id


def criar_checkout_session(db: Session, usuario: Usuario, price_id: str, origin: str | None = None) -> dict:
    """Cria uma Stripe Embedded Checkout Session (suporta assinatura recorrente e pagamento avulso/Pix)."""
    customer_id = _obter_ou_criar_customer(db, usuario)

    base_url = (origin or settings.frontend_url).rstrip("/")

    # Verificar o tipo de preço no Stripe (recorrente ou avulso)
    is_recurring = True
    try:
        price_obj = stripe.Price.retrieve(price_id)
        if price_obj.get("type") == "one_time":
            is_recurring = False
    except Exception:
        pass

    params = {
        "customer": customer_id,
        "ui_mode": "embedded" if is_recurring else "embedded_page",
        "mode": "subscription" if is_recurring else "payment",
        "line_items": [{"price": price_id, "quantity": 1}],
        "return_url": f"{base_url}/configuracoes?assinatura=sucesso&session_id={{CHECKOUT_SESSION_ID}}",
        "allow_promotion_codes": True,
    }

    if is_recurring:
        params["subscription_data"] = {"metadata": {"usuario_id": str(usuario.id)}}
    else:
        params["payment_intent_data"] = {"metadata": {"usuario_id": str(usuario.id), "price_id": price_id}}
        params["metadata"] = {"usuario_id": str(usuario.id), "price_id": price_id}

    pm_config = settings.stripe_payment_method_configuration.strip()
    if pm_config and pm_config.startswith("pmc_"):
        params["payment_method_configuration"] = pm_config

    try:
        session = stripe.checkout.Session.create(**params)
    except stripe.error.InvalidRequestError as err:
        if "payment_method_configuration" in str(err) and "payment_method_configuration" in params:
            params.pop("payment_method_configuration", None)
            session = stripe.checkout.Session.create(**params)
        else:
            raise err

    return {
        "client_secret": session.client_secret,
        "checkout_url": session.url
    }


def processar_webhook_event(payload: bytes, sig_header: str) -> dict:
    """Processa um evento de webhook do Stripe."""
    event = stripe.Webhook.construct_event(
        payload, sig_header, settings.stripe_webhook_secret
    )
    return event


def ativar_plano_pro(db: Session, usuario_id: int, subscription_id: str, current_period_end: int) -> None:
    """Marca o usuario como PRO com data de expiracao."""
    from sqlalchemy import select

    usuario = db.execute(select(Usuario).where(Usuario.id == usuario_id)).scalar_one_or_none()
    if not usuario:
        return

    usuario.plano = "PRO"
    usuario.stripe_subscription_id = subscription_id
    usuario.plano_expira_em = datetime.fromtimestamp(current_period_end, tz=timezone.utc)
    db.commit()


def desativar_plano_pro(db: Session, usuario_id: int) -> None:
    """Retorna o usuario para o plano FREE."""
    from sqlalchemy import select

    usuario = db.execute(select(Usuario).where(Usuario.id == usuario_id)).scalar_one_or_none()
    if not usuario:
        return

    usuario.plano = "FREE"
    usuario.plano_expira_em = None
    usuario.stripe_subscription_id = None
    db.commit()


def cancelar_assinatura_stripe(subscription_id: str) -> None:
    """Cancela uma assinatura no Stripe (ao final do periodo)."""
    stripe.Subscription.modify(
        subscription_id,
        cancel_at_period_end=True,
    )


def obter_usuario_id_de_subscription(subscription: dict) -> int | None:
    """Extrai o usuario_id dos metadados de uma subscription."""
    metadata = subscription.get("metadata", {})
    uid = metadata.get("usuario_id")
    if uid:
        try:
            return int(uid)
        except (ValueError, TypeError):
            pass

    # Fallback: buscar pelo customer_id
    return None


def obter_usuario_por_customer_id(db: Session, customer_id: str) -> Usuario | None:
    """Busca um usuario pelo stripe_customer_id."""
    from sqlalchemy import select

    return db.execute(
        select(Usuario).where(Usuario.stripe_customer_id == customer_id)
    ).scalar_one_or_none()


def criar_checkout_infinitepay(db: Session, usuario: Usuario, plano: str, origin: str | None = None) -> dict:
    """Cria um link de pagamento dinamico via API do Checkout Integrado da InfinitePay."""
    import time
    import httpx

    base_url = (origin or settings.frontend_url).rstrip("/")
    redirect_url = f"{base_url}/configuracoes?assinatura=sucesso&gateway=infinitepay"
    webhook_url = f"{base_url}/assinaturas/webhook/infinitepay"

    if plano == "anual":
        price_cents = 8990
        description = "Gestão Motoca PRO - Plano Anual"
    elif plano == "mensal":
        price_cents = 990
        description = "Gestão Motoca PRO - Plano Mensal"
    else:
        price_cents = 990
        description = "Gestão Motoca PRO - Pix Avulso (30 dias)"

    order_nsu = f"user_{usuario.id}_{int(time.time())}"

    payload = {
        "handle": settings.infinitepay_handle,
        "redirect_url": redirect_url,
        "webhook_url": webhook_url,
        "order_nsu": order_nsu,
        "customer": {
            "name": usuario.nome,
            "email": usuario.email,
        },
        "items": [
            {
                "quantity": 1,
                "price": price_cents,
                "description": description,
            }
        ],
    }

    try:
        url_api = f"{settings.infinitepay_api_url.rstrip('/')}/links"
        response = httpx.post(url_api, json=payload, timeout=10.0)
        if response.status_code in (200, 201):
            data = response.json()
            checkout_url = data.get("url")
            if checkout_url:
                return {"checkout_url": checkout_url, "order_nsu": order_nsu}
    except Exception as e:
        print(f"[InfinitePay] Erro ao chamar API de links: {e}")

    # Fallback caso a API falhe ou não retorne URL
    return {"checkout_url": settings.infinitepay_checkout_url, "order_nsu": order_nsu}


def processar_webhook_infinitepay(db: Session, payload: dict) -> dict:
    """Processa o webhook enviado pela InfinitePay ao confirmar um pagamento."""
    order_nsu = payload.get("order_nsu", "")
    transaction_nsu = payload.get("transaction_nsu") or payload.get("invoice_slug") or "tx_infinitepay"
    amount = payload.get("paid_amount") or payload.get("amount") or 0

    usuario_id = None

    if order_nsu and order_nsu.startswith("user_"):
        parts = order_nsu.split("_")
        if len(parts) >= 2:
            try:
                usuario_id = int(parts[1])
            except ValueError:
                pass

    if not usuario_id:
        customer = payload.get("customer", {})
        email = customer.get("email") if isinstance(customer, dict) else None
        if email:
            from sqlalchemy import select
            u = db.execute(select(Usuario).where(Usuario.email == email)).scalar_one_or_none()
            if u:
                usuario_id = u.id

    if not usuario_id:
        return {"success": False, "message": "Pedido não encontrado"}

    from datetime import timedelta
    import logging
    logger = logging.getLogger("app.services.assinatura_service")

    dias = 365 if amount >= 8900 else 30
    expira_em_ts = int((datetime.now(timezone.utc) + timedelta(days=dias)).timestamp())

    ativar_plano_pro(db, usuario_id, f"infinitepay_{transaction_nsu}", expira_em_ts)
    msg_log = f"[WEBHOOK INFINITEPAY RECEBIDO & PROCESSADO] usuario_id={usuario_id}, tx_nsu={transaction_nsu}, order_nsu={order_nsu}, amount={amount}, dias={dias}"
    logger.info(msg_log)
    print(msg_log)

    return {"success": True, "message": None}



def gerar_pix_direto(db: Session, usuario: Usuario, plano: str, origin: str | None = None) -> dict:
    """Gera cobrança Pix com QR Code e Copia e Cola diretamente no app."""
    import time
    from urllib.parse import quote

    order_nsu = f"user_{usuario.id}_{int(time.time())}"

    if plano == "anual":
        amount_cents = 8990
        valor_fmt = "R$ 89,90"
        desc = "Gestão Motoca PRO (Anual)"
    elif plano == "mensal":
        amount_cents = 990
        valor_fmt = "R$ 9,90"
        desc = "Gestão Motoca PRO (Mensal)"
    else:
        amount_cents = 990
        valor_fmt = "R$ 9,99"
        desc = "Gestão Motoca PRO (Pix Avulso 30 dias)"

    qr_code_text = ""
    qr_code_url = ""
    fallback_url = settings.infinitepay_checkout_url

    if settings.stripe_secret_key:
        try:
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency="brl",
                payment_method_types=["pix"],
                description=desc,
                metadata={"usuario_id": str(usuario.id), "order_nsu": order_nsu, "plano": plano},
            )
            pix_display = intent.get("next_action", {}).get("pix_display", {})
            qr_code_text = pix_display.get("qr_code_text", "")
            qr_code_url = pix_display.get("qr_code_url", "")
        except Exception as e:
            print(f"[Pix] Stripe Pix não pôde ser gerado: {e}")

    inf_res = criar_checkout_infinitepay(db, usuario, plano, origin=origin)
    if inf_res.get("checkout_url"):
        fallback_url = inf_res["checkout_url"]
        if inf_res.get("order_nsu"):
            order_nsu = inf_res["order_nsu"]

    if not qr_code_text:
        qr_code_text = fallback_url

    if not qr_code_url and qr_code_text:
        qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?size=260x260&data={quote(qr_code_text)}"

    from datetime import timedelta
    expires_at = (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat()

    return {
        "qr_code_text": qr_code_text,
        "qr_code_url": qr_code_url,
        "order_nsu": order_nsu,
        "valor_formatado": valor_fmt,
        "expires_at": expires_at,
        "checkout_url_fallback": fallback_url,
    }


def checar_status_pix(db: Session, usuario: Usuario, order_nsu: str) -> dict:
    """Verifica se o pagamento Pix correspondente ao order_nsu foi concluído."""
    from sqlalchemy import select

    u = db.execute(select(Usuario).where(Usuario.id == usuario.id)).scalar_one_or_none()
    if not u:
        return {"pago": False, "plano": "FREE"}

    if u.plano == "PRO":
        return {"pago": True, "plano": "PRO"}

    return {"pago": False, "plano": u.plano}


def confirmar_retorno_infinitepay(db: Session, usuario: Usuario, order_nsu: str | None = None, transaction_nsu: str | None = None, plano: str | None = None) -> dict:
    """Confirma a ativacao do plano PRO quando o usuario retorna do checkout da InfinitePay."""
    from datetime import timedelta
    import logging

    logger = logging.getLogger("app.services.assinatura_service")

    target_user_id = usuario.id
    if order_nsu and order_nsu.startswith("user_"):
        parts = order_nsu.split("_")
        if len(parts) >= 2:
            try:
                target_user_id = int(parts[1])
            except ValueError:
                pass

    dias = 365 if (plano == "anual" or (order_nsu and "anual" in order_nsu)) else 30
    expira_em_ts = int((datetime.now(timezone.utc) + timedelta(days=dias)).timestamp())
    tx_id = transaction_nsu or order_nsu or "return_infinitepay"

    ativar_plano_pro(db, target_user_id, f"infinitepay_{tx_id}", expira_em_ts)

    msg_log = f"[PAGAMENTO REGISTRADO - INFINITEPAY] usuario_id={target_user_id}, tx_id={tx_id}, order_nsu={order_nsu}, dias={dias}, expira_em_ts={expira_em_ts}"
    logger.info(msg_log)
    print(msg_log)

    return {"sucesso": True, "plano": "PRO", "dias": dias}




