from sqlalchemy import String, Integer, Boolean, DateTime, Numeric, func, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class MotoVersao(Base):
    __tablename__ = "motos_versoes"
    __table_args__ = (UniqueConstraint("moto_modelo_id", "ano", name="uq_motos_versoes_modelo_ano"),)

    id: Mapped[int] = mapped_column(primary_key=True)

    moto_modelo_id: Mapped[int] = mapped_column(ForeignKey("motos_modelos.id", ondelete="CASCADE"), nullable=False)
    ano: Mapped[int] = mapped_column(Integer, nullable=False)

    tipo_combustivel: Mapped[str | None] = mapped_column(String(30), nullable=True)
    consumo_medio_km_l: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    capacidade_tanque_l: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)

    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    data_criacao: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    moto_modelo = relationship("MotoModelo")