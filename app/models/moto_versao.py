from sqlalchemy import String, Integer, Boolean, DateTime, Numeric, func, ForeignKey, UniqueConstraint, Column
from sqlalchemy.orm import relationship

from app.database.base import Base


class MotoVersao(Base):
    __tablename__ = "motos_versoes"
    __table_args__ = (UniqueConstraint("moto_modelo_id", "ano", name="uq_motos_versoes_modelo_ano"),)

    id = Column(Integer, primary_key=True)

    moto_modelo_id = Column(Integer, ForeignKey("motos_modelos.id", ondelete="CASCADE"), nullable=False)
    ano = Column(Integer, nullable=False)

    tipo_combustivel = Column(String(30), nullable=True)
    consumo_medio_km_l = Column(Numeric(6, 2), nullable=True)
    capacidade_tanque_l = Column(Numeric(6, 2), nullable=True)

    ativo = Column(Boolean, nullable=False, server_default="true")
    data_criacao = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    moto_modelo = relationship("MotoModelo")