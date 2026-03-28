from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
)

from app.database.base import Base


class Meta(Base):
    __tablename__ = "metas"
    __table_args__ = (
        CheckConstraint("tipo IN ('GANHO', 'DESPESA')", name="ck_metas_tipo"),
        CheckConstraint("periodo IN ('SEMANAL', 'MENSAL')", name="ck_metas_periodo"),
        CheckConstraint("valor_meta > 0", name="ck_metas_valor_meta_positivo"),
    )

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)

    nome = Column(String(80), nullable=False)
    tipo = Column(String(20), nullable=False)
    periodo = Column(String(20), nullable=False)
    valor_meta = Column(Numeric(10, 2), nullable=False)
    ativa = Column(Boolean, nullable=False, server_default="true")

    data_criacao = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
