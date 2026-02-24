from sqlalchemy import String, Integer, Boolean, DateTime, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class MotoModelo(Base):
    __tablename__ = "motos_modelos"
    __table_args__ = (UniqueConstraint("marca", "modelo", name="uq_motos_modelos_marca_modelo"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    marca: Mapped[str] = mapped_column(String(80), nullable=False)
    modelo: Mapped[str] = mapped_column(String(120), nullable=False)
    cilindrada_cc: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    data_criacao: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)