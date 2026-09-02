from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CriarCheckoutEntrada(BaseModel):
    price_id: str


class CheckoutResposta(BaseModel):
    client_secret: str
    checkout_url: Optional[str] = None


class CriarCheckoutInfinitepayEntrada(BaseModel):
    plano: str = "pix_avulso"


class CheckoutInfinitepayResposta(BaseModel):
    checkout_url: str
    order_nsu: Optional[str] = None


class CriarPixDiretoEntrada(BaseModel):
    plano: str = "pix_avulso"


class PixDiretoResposta(BaseModel):
    qr_code_text: str
    qr_code_url: str
    order_nsu: str
    valor_formatado: str
    expires_at: Optional[str] = None
    checkout_url_fallback: Optional[str] = None


class ChecarPixEntrada(BaseModel):
    order_nsu: str


class ChecarPixResposta(BaseModel):
    pago: bool
    plano: str



class AssinaturaStatusResposta(BaseModel):
    plano: str
    plano_expira_em: Optional[datetime] = None
    stripe_subscription_id: Optional[str] = None
    em_trial: bool = False
    dias_trial_restantes: int = 0
    stripe_publishable_key: str = ""
