from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, ForeignKey, CheckConstraint, func

from app.database.base import Base


class Lancamento(Base):
    __tablename__ = "lancamentos"
    __table_args__ = (
        CheckConstraint("tipo IN ('GANHO', 'DESPESA')", name="ck_lancamentos_tipo"),
        CheckConstraint("valor > 0", name="ck_lancamentos_valor_positivo"),
        CheckConstraint(
            "periodicidade_ganho IS NULL OR periodicidade_ganho IN ('DIARIO', 'SEMANAL', 'CORRIDA')",
            name="ck_lancamentos_periodicidade_ganho",
        ),
        CheckConstraint(
            "minutos_corrida IS NULL OR minutos_corrida > 0",
            name="ck_lancamentos_minutos_corrida_positivo",
        ),
        CheckConstraint(
            "km_corrida IS NULL OR km_corrida > 0",
            name="ck_lancamentos_km_corrida_positivo",
        ),
    )

    id = Column(Integer, primary_key=True)

    usuario_id = Column(Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False
    )

    moto_usuario_id = Column(Integer,
        ForeignKey("motos_usuario.id", ondelete="SET NULL"),
        nullable=True
    )

    categoria_id = Column(Integer,
        ForeignKey("categorias.id"),
        nullable=False
    )

    tipo = Column(String(20), nullable=False)
    valor = Column(Numeric(10, 2), nullable=False)
    descricao = Column(String(255), nullable=True)
    periodicidade_ganho = Column(String(20), nullable=True)
    minutos_corrida = Column(Integer, nullable=True)
    km_corrida = Column(Numeric(8, 2), nullable=True)

    data_lancamento = Column(Date, nullable=False, server_default=func.current_date())
    data_criacao = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
