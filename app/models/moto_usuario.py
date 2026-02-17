from sqlalchemy import String, Integer, DateTime, func, CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class MotoUsuario(Base):
    __tablename__ = "motos_usuario"
    __table_args__ = (
        CheckConstraint(
            "(moto_catalogo_id IS NOT NULL AND marca_manual IS NULL AND modelo_manual IS NULL) "
            "OR (moto_catalogo_id IS NULL AND marca_manual IS NOT NULL AND modelo_manual IS NOT NULL)",
            name="ck_origem_moto",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    moto_catalogo_id: Mapped[int | None] = mapped_column(ForeignKey("motos_catalogo.id"), nullable=True)

    marca_manual: Mapped[str | None] = mapped_column(String(80), nullable=True)
    modelo_manual: Mapped[str | None] = mapped_column(String(120), nullable=True)

    ano: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cor: Mapped[str | None] = mapped_column(String(40), nullable=True)
    km_atual: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")

    data_cadastro: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # relacionamentos (opcional agora, mas útil)
    usuario = relationship("Usuario")
    moto_catalogo = relationship("MotoCatalogo")
