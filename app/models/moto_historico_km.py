from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)

from app.database.base import Base


class MotoHistoricoKm(Base):
    __tablename__ = "motos_historico_km"

    id = Column(Integer, primary_key=True)

    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
    )

    moto_usuario_id = Column(
        Integer,
        ForeignKey("motos_usuario.id", ondelete="CASCADE"),
        nullable=False,
    )

    km = Column(Integer, nullable=False)

    origem = Column(String(30), nullable=False, default="ATUALIZACAO_RAPIDA")

    situacao = Column(String(20), nullable=False, default="ATIVO", server_default="ATIVO")
    data = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    data_criacao = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
