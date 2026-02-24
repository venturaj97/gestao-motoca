from sqlalchemy import String, Integer, DateTime, func, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class MotoUsuario(Base):
    __tablename__ = "motos_usuario"

    __table_args__ = (
        CheckConstraint(
            "(moto_versao_id IS NOT NULL AND marca_manual IS NULL AND modelo_manual IS NULL) "
            "OR "
            "(moto_versao_id IS NULL AND marca_manual IS NOT NULL AND modelo_manual IS NOT NULL)",
            name="ck_origem_moto"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False
    )

    moto_versao_id: Mapped[int | None] = mapped_column(
        ForeignKey("motos_versoes.id"),
        nullable=True
    )

    marca_manual: Mapped[str | None] = mapped_column(String(80), nullable=True)
    modelo_manual: Mapped[str | None] = mapped_column(String(120), nullable=True)
    ano_manual: Mapped[int | None] = mapped_column(Integer, nullable=True)

    km_atual: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    cor: Mapped[str | None] = mapped_column(String(40), nullable=True)

    data_cadastro: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    usuario = relationship("Usuario")
    moto_versao = relationship("MotoVersao")