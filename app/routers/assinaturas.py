"""Rotas de assinatura PRO (Stripe)."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.session import get_db
from app.dependencies import get_usuario_logado
from app.models.usuario import Usuario
from app.schemas.assinatura import AssinaturaStatusResposta, CheckoutResposta, CriarCheckoutEntrada
from app.services.assinatura_service import (
    ativar_plano_pro,
    cancelar_assinatura_stripe,
    criar_checkout_session,
    desativar_plano_pro,
    obter_usuario_id_de_subscription,
    obter_usuario_por_customer_id,
    processar_webhook_event,
)

router = APIRouter(prefix="/assinaturas", tags=["assinaturas"])


@router.post("/checkout", response_model=CheckoutResposta)
def rota_criar_checkout(
    dados: CriarCheckoutEntrada,
    request: Request,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_logado),
):
    """Cria uma sessão de checkout do Stripe e retorna a URL."""
    if dados.price_id and dados.price_id.startswith("prod_"):
        raise HTTPException(
            status_code=400,
            detail=f"O ID '{dados.price_id}' configurado é um ID de Produto (prod_). Por favor, use o ID do Preço (price_...) gerado dentro desse produto no Stripe."
        )

    prices_validos = [
        settings.stripe_price_mensal,
        settings.stripe_price_anual,
        settings.stripe_price_pix_avulso,
    ]
    prices_validos = [p for p in prices_validos if p]
    if dados.price_id not in prices_validos:
        raise HTTPException(status_code=400, detail="Plano invalido")

    # Extrair origem real da requisição (necessário para celular via IP local ou túnel Cloudflare)
    origin_header = request.headers.get("origin") or request.headers.get("referer")
    request_origin = None
    if origin_header:
        from urllib.parse import urlparse
        parsed = urlparse(origin_header)
        request_origin = f"{parsed.scheme}://{parsed.netloc}"

    res = criar_checkout_session(db, usuario, dados.price_id, origin=request_origin)
    return CheckoutResposta(
        client_secret=res["client_secret"],
        checkout_url=res.get("checkout_url")
    )


@router.get("/status", response_model=AssinaturaStatusResposta)
def rota_status_assinatura(
    usuario: Usuario = Depends(get_usuario_logado),
):
    """Retorna o status da assinatura do usuario."""
    em_trial = False
    dias_trial_restantes = 0

    if usuario.plano == "FREE" and usuario.data_criacao:
        dt_criacao = usuario.data_criacao
        if dt_criacao.tzinfo is None:
            dt_criacao = dt_criacao.replace(tzinfo=timezone.utc)
        dias = (datetime.now(timezone.utc) - dt_criacao).days
        if dias <= 7:
            em_trial = True
            dias_trial_restantes = max(0, 7 - dias)

    return AssinaturaStatusResposta(
        plano=usuario.plano,
        plano_expira_em=usuario.plano_expira_em,
        stripe_subscription_id=usuario.stripe_subscription_id,
        em_trial=em_trial,
        dias_trial_restantes=dias_trial_restantes,
        stripe_publishable_key=settings.stripe_publishable_key,
    )


@router.post("/cancelar")
def rota_cancelar_assinatura(
    usuario: Usuario = Depends(get_usuario_logado),
):
    """Cancela a assinatura PRO (encerra ao final do periodo pago)."""
    if not usuario.stripe_subscription_id:
        raise HTTPException(status_code=400, detail="Nenhuma assinatura ativa")

    cancelar_assinatura_stripe(usuario.stripe_subscription_id)
    return {"mensagem": "Assinatura sera cancelada ao final do periodo atual."}


@router.get("/precos")
def rota_listar_precos():
    """Retorna os IDs de preço do Stripe para o frontend."""
    pix_price = settings.stripe_price_pix_avulso or settings.stripe_price_mensal
    return {
        "mensal": {
            "price_id": settings.stripe_price_mensal,
            "valor": "R$ 9,90/mês",
        },
        "anual": {
            "price_id": settings.stripe_price_anual,
            "valor": "R$ 89,90/ano (~R$ 7,49/mês)",
        },
        "pix_avulso": {
            "price_id": pix_price,
            "valor": "R$ 9,99 (30 dias via Pix)",
        },
        "stripe_publishable_key": settings.stripe_publishable_key,
    }


@router.post("/webhook")
async def rota_stripe_webhook(
    request: Request,
    stripe_signature: str = Header(alias="stripe-signature"),
    db: Session = Depends(get_db),
):
    """Recebe eventos do Stripe via webhook."""
    payload = await request.body()

    try:
        event = processar_webhook_event(payload, stripe_signature)
    except Exception:
        raise HTTPException(status_code=400, detail="Webhook inválido")

    event_type = event["type"]
    data_obj = event["data"]["object"]

    if event_type == "checkout.session.completed":
        subscription_id = data_obj.get("subscription")
        if subscription_id:
            # Assinatura Recorrente
            import stripe as stripe_lib
            sub = stripe_lib.Subscription.retrieve(subscription_id)
            usuario_id = obter_usuario_id_de_subscription(sub)

            if not usuario_id:
                customer_id = data_obj.get("customer")
                u = obter_usuario_por_customer_id(db, customer_id)
                if u:
                    usuario_id = u.id

            if usuario_id:
                ativar_plano_pro(db, usuario_id, subscription_id, sub["current_period_end"])
        else:
            # Pagamento Avulso (Pix, PicPay, Cartão Avulso)
            metadata = data_obj.get("metadata", {})
            usuario_id = metadata.get("usuario_id")
            if not usuario_id:
                customer_id = data_obj.get("customer")
                u = obter_usuario_por_customer_id(db, customer_id)
                if u:
                    usuario_id = u.id
            else:
                try:
                    usuario_id = int(usuario_id)
                except (ValueError, TypeError):
                    usuario_id = None

            if usuario_id:
                from datetime import timedelta
                price_id = metadata.get("price_id")
                dias = 365 if price_id == settings.stripe_price_anual else 30
                expira_em_ts = int((datetime.now(timezone.utc) + timedelta(days=dias)).timestamp())
                ativar_plano_pro(db, usuario_id, None, expira_em_ts)

    elif event_type == "invoice.payment_succeeded":
        subscription_id = data_obj.get("subscription")
        if subscription_id:
            import stripe as stripe_lib
            sub = stripe_lib.Subscription.retrieve(subscription_id)
            usuario_id = obter_usuario_id_de_subscription(sub)

            if not usuario_id:
                customer_id = data_obj.get("customer")
                u = obter_usuario_por_customer_id(db, customer_id)
                if u:
                    usuario_id = u.id

            if usuario_id:
                ativar_plano_pro(db, usuario_id, subscription_id, sub["current_period_end"])

    elif event_type in (
        "customer.subscription.deleted",
        "customer.subscription.paused",
    ):
        subscription_id = data_obj.get("id")
        usuario_id = obter_usuario_id_de_subscription(data_obj)

        if not usuario_id:
            customer_id = data_obj.get("customer")
            u = obter_usuario_por_customer_id(db, customer_id)
            if u:
                usuario_id = u.id

        if usuario_id:
            desativar_plano_pro(db, usuario_id)

    return {"status": "ok"}
