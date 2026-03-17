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


class Abastecimento(Base):
    __tablename__ = "abastecimentos"
    __table_args__ = (
        CheckConstraint("litros > 0", name="ck_abastecimentos_litros_positivos"),
        CheckConstraint("valor_total > 0", name="ck_abastecimentos_valor_total_positivo"),
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

    litros = Column(Numeric(6, 2), nullable=False)
    valor_total = Column(Numeric(10, 2), nullable=False)
    valor_litro = Column(Numeric(8, 3), nullable=False)

    km_atual = Column(Integer, nullable=True)

    data_abastecimento = Column(
        Date,
        nullable=False,
        server_default=func.current_date(),
    )

    posto = Column(String(120), nullable=True)
    tipo_combustivel = Column(String(40), nullable=True)

    data_criacao = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

