"""cria tabela cofres para gestão de reservas e autoguarda percentual

Revision ID: 0012_tabela_cofres
Revises: 0011_metas_dias_trabalho_cofres
Create Date: 2026-08-27 00:00:12.000000
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = "0012_tabela_cofres"
down_revision: Union[str, None] = "0011_metas_dias_trabalho_cofres"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "cofres",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=80), nullable=False),
        sa.Column("categoria", sa.String(length=50), nullable=False),
        sa.Column("valor_meta", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("saldo_atual", sa.Numeric(precision=10, scale=2), nullable=False, server_default="0.00"),
        sa.Column("porcentagem_autoguarda", sa.Numeric(precision=5, scale=2), nullable=False, server_default="0.00"),
        sa.Column("ativa", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("situacao", sa.String(length=20), nullable=False, server_default="ATIVO"),
        sa.Column("data", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("data_criacao", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("valor_meta > 0", name="ck_cofres_valor_meta_positivo"),
        sa.CheckConstraint("saldo_atual >= 0", name="ck_cofres_saldo_atual_nao_negativo"),
        sa.CheckConstraint("porcentagem_autoguarda >= 0 AND porcentagem_autoguarda <= 100", name="ck_cofres_porcentagem_valida"),
    )
    op.create_index("ix_cofres_usuario_id", "cofres", ["usuario_id"])


def downgrade() -> None:
    op.drop_index("ix_cofres_usuario_id", table_name="cofres")
    op.drop_table("cofres")
