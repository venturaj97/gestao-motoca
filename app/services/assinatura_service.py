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


def criar_checkout_session(db: Session, usuario: Usuario, price_id: str) -> dict:
    """Cria uma Stripe Embedded Checkout Session e retorna client_secret."""
    customer_id = _obter_ou_criar_customer(db, usuario)

    session = stripe.checkout.Session.create(
        customer=customer_id,
        ui_mode="embedded",
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        return_url=f"{settings.frontend_url}/configuracoes?assinatura=sucesso&session_id={{CHECKOUT_SESSION_ID}}",
        subscription_data={
            "metadata": {"usuario_id": str(usuario.id)},
        },
        allow_promotion_codes=True,
    )

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
