from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)

from app.database.base import Base


class Categoria(Base):
    __tablename__ = "categorias"
    __table_args__ = (
        UniqueConstraint("usuario_id", "nome", "tipo", name="uq_categorias_usuario_nome_tipo"),
        CheckConstraint("tipo IN ('GANHO', 'DESPESA')", name="ck_categorias_tipo"),
        CheckConstraint(
            "grupo_despesa IS NULL OR grupo_despesa IN ('GERAL', 'MANUTENCAO', 'ABASTECIMENTO', 'IMPOSTO')",
            name="ck_categorias_grupo_despesa",
        ),
    )

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=True, index=True)
    nome = Column(String(100), nullable=False)
    tipo = Column(String(20), nullable=False)
    grupo_despesa = Column(String(20), nullable=True)
    ativo = Column(Boolean, nullable=False, server_default="true")
    data_criacao = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
