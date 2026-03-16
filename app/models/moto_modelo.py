from sqlalchemy import String, Integer, Boolean, DateTime, func, UniqueConstraint, Column

from app.database.base import Base


class MotoModelo(Base):
    __tablename__ = "motos_modelos"
    __table_args__ = (UniqueConstraint("marca", "modelo", name="uq_motos_modelos_marca_modelo"),)

    id = Column(Integer, primary_key=True)
    marca = Column(String(80), nullable=False)
    modelo = Column(String(120), nullable=False)
    cilindrada_cc = Column(Integer, nullable=True)
    ativo = Column(Boolean, nullable=False, server_default="true")
    data_criacao = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)