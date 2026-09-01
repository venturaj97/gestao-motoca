from sqlalchemy import Boolean, Column, DateTime, Integer, String, func

from app.database.base import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    nome = Column(String(120), nullable=False)
    email = Column(String(180), unique=True, index=True, nullable=False)
    senha = Column(String(255), nullable=False)
    email_confirmado = Column(Boolean, default=False, nullable=False, server_default="false")
    situacao = Column(String(20), nullable=False, default="ATIVO", server_default="ATIVO")
    data = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    data_criacao = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # ── Plano / Assinatura ──
    plano = Column(String(20), nullable=False, default="FREE", server_default="FREE")
    plano_expira_em = Column(DateTime(timezone=True), nullable=True)
    stripe_customer_id = Column(String(100), nullable=True)
    stripe_subscription_id = Column(String(100), nullable=True)

