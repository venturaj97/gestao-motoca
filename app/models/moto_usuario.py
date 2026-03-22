from sqlalchemy import String, Integer, DateTime, func, ForeignKey, CheckConstraint, Column, Boolean
from sqlalchemy.orm import relationship

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

    id = Column(Integer, primary_key=True)

    usuario_id = Column(Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False
    )

    moto_versao_id = Column(Integer,
        ForeignKey("motos_versoes.id"),
        nullable=True
    )

    marca_manual = Column(String(80), nullable=True)
    modelo_manual = Column(String(120), nullable=True)
    ano_manual = Column(Integer, nullable=True)

    km_atual = Column(Integer, nullable=False, default=0)
    cor = Column(String(40), nullable=True)

    # Varias motos podem estar ativas ao mesmo tempo; novas entram ativas por padrao
    ativa = Column(Boolean, nullable=False, server_default="true", default=True)

    data_cadastro = Column(DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    usuario = relationship("Usuario")
    moto_versao = relationship("MotoVersao")