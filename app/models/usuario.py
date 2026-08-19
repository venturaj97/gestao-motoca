# pyrefly: ignore [missing-import]
from sqlalchemy import Boolean, Column, DateTime, Integer, String, func

from app.database.base import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    nome = Column(String(120), nullable=False)
    email = Column(String(180), unique=True, index=True, nullable=False)
    senha = Column(String(255), nullable=False)
    email_confirmado = Column(Boolean, default=False, nullable=False, server_default="false")
    data_criacao = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
