from sqlalchemy import (
    Column,
    Integer,
    Numeric,
    Date,
    DateTime,
    String,
    ForeignKey,
    CheckConstraint,
    func,
)

from app.database.base import Base


class Manutencao(Base):
    __tablename__ = "manutencoes"
    __table_args__ = (
        CheckConstraint("valor_total > 0", name="ck_manutencoes_valor_total_positivo"),
    )

    id = Column(Integer, primary_key=True)

    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
    )

    moto_usuario_id = Column(
        Integer,
        ForeignKey("motos_usuario.id", ondelete="SET NULL"),
        nullable=True,
    )

    lancamento_id = Column(
        Integer,
        ForeignKey("lancamentos.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    valor_total = Column(Numeric(10, 2), nullable=False)

    km_atual = Column(Integer, nullable=True)

    data_manutencao = Column(
        Date,
        nullable=False,
        server_default=func.current_date(),
    )

    descricao_servico = Column(String(255), nullable=True)
    oficina = Column(String(120), nullable=True)
    tipo_servico = Column(String(80), nullable=True)

    data_criacao = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

