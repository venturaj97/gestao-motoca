from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, UniqueConstraint, CheckConstraint

from app.database.base import Base


class Categoria(Base):
    __tablename__ = "categorias"
    __table_args__ = (
        UniqueConstraint("nome", "tipo", name="uq_categorias_nome_tipo"),
        CheckConstraint("tipo IN ('GANHO', 'DESPESA')", name="ck_categorias_tipo"),
    )

    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    tipo = Column(String(20), nullable=False)
    ativo = Column(Boolean, nullable=False, server_default="true")
    data_criacao = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)