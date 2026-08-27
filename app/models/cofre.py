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


class Cofre(Base):
    __tablename__ = "cofres"
    __table_args__ = (
        CheckConstraint("valor_meta > 0", name="ck_cofres_valor_meta_positivo"),
        CheckConstraint("saldo_atual >= 0", name="ck_cofres_saldo_atual_nao_negativo"),
        CheckConstraint("porcentagem_autoguarda >= 0 AND porcentagem_autoguarda <= 100", name="ck_cofres_porcentagem_valida"),
    )

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)

    nome = Column(String(80), nullable=False)
    categoria = Column(String(50), nullable=False)  # PNEU, SEGURO, IPVA, REVISAO, RESERVA, OUTROS
    valor_meta = Column(Numeric(10, 2), nullable=False)
    saldo_atual = Column(Numeric(10, 2), nullable=False, default=0.00, server_default="0.00")
    porcentagem_autoguarda = Column(Numeric(5, 2), nullable=False, default=0.00, server_default="0.00")
    ativa = Column(Boolean, nullable=False, default=True, server_default="true")
    situacao = Column(String(20), nullable=False, default="ATIVO", server_default="ATIVO")
    data = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    data_criacao = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
