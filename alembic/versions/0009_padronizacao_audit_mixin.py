"""padronizacao audit mixin

Revision ID: 0009_padronizacao_audit_mixin
Revises: 0008_email_confirmado
Create Date: 2026-08-19 00:00:09.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0009_padronizacao_audit_mixin"
down_revision: Union[str, None] = "0008_email_confirmado"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


tabelas = [
    "usuarios",
    "motos_usuario",
    "categorias",
    "lancamentos",
    "abastecimentos",
    "manutencoes",
    "metas",
    "recuperacoes_senha",
]


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    for tabela in tabelas:
        columns = [col["name"] for col in inspector.get_columns(tabela)]
        if "situacao" not in columns:
            op.add_column(
                tabela,
                sa.Column("situacao", sa.String(length=20), server_default="ATIVO", nullable=False),
            )
        if "data" not in columns:
            op.add_column(
                tabela,
                sa.Column("data", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            )
        if "data_criacao" not in columns:
            if "data_cadastro" in columns:
                op.alter_column(tabela, "data_cadastro", new_column_name="data_criacao")
            else:
                op.add_column(
                    tabela,
                    sa.Column("data_criacao", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
                )


def downgrade() -> None:
    for tabela in tabelas:
        op.drop_column(tabela, "data")
        op.drop_column(tabela, "situacao")
