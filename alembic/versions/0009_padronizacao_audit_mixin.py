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
    for tabela in tabelas:
        op.add_column(
            tabela,
            sa.Column("situacao", sa.String(length=20), server_default="ATIVO", nullable=False),
        )
        op.add_column(
            tabela,
            sa.Column("data", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        )


def downgrade() -> None:
    for tabela in tabelas:
        op.drop_column(tabela, "data")
        op.drop_column(tabela, "situacao")
