from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CriarCheckoutEntrada(BaseModel):
    price_id: str


class CheckoutResposta(BaseModel):
    client_secret: str
    checkout_url: Optional[str] = None


class AssinaturaStatusResposta(BaseModel):
    plano: str
    plano_expira_em: Optional[datetime] = None
    stripe_subscription_id: Optional[str] = None
    em_trial: bool = False
    dias_trial_restantes: int = 0
    stripe_publishable_key: str = ""
