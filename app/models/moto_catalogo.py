from sqlalchemy import String, Integer, Boolean, DateTime, Numeric, func, UniqueConstraint, Column

from app.database.base import Base


class MotoCatalogo(Base):
    __tablename__ = "motos_catalogo"
    __table_args__ = (UniqueConstraint("marca", "modelo", name="uq_motos_catalogo_marca_modelo"),)

    id = Column(Integer, primary_key=True)
    marca = Column(String(80), nullable=False)
    modelo = Column(String(120), nullable=False)
    cilindrada_cc = Column(Integer, nullable=True)
    tipo_combustivel = Column(String(30), nullable=True)
    consumo_medio_km_l = Column(Numeric(6, 2), nullable=True)
    capacidade_tanque_l = Column(Numeric(6, 2), nullable=True)
    ativo = Column(Boolean, nullable=False, server_default="true")
    data_criacao = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
