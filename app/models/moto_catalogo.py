from sqlalchemy import String, Integer, Boolean, DateTime, Numeric, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class MotoCatalogo(Base):
    __tablename__ = "motos_catalogo"
    __table_args__ = (UniqueConstraint("marca", "modelo", name="uq_motos_catalogo_marca_modelo"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    marca: Mapped[str] = mapped_column(String(80), nullable=False)
    modelo: Mapped[str] = mapped_column(String(120), nullable=False)
    cilindrada_cc: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tipo_combustivel: Mapped[str | None] = mapped_column(String(30), nullable=True)
    consumo_medio_km_l: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    capacidade_tanque_l: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    data_criacao: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
