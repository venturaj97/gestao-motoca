"""cria tabela de metas por usuario

Revision ID: 0005_metas_usuario
Revises: 0004_lanc_periodo_diasem
Create Date: 2026-03-28 00:00:04.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0005_metas_usuario"
down_revision: Union[str, None] = "0004_lanc_periodo_diasem"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "metas",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False),
        sa.Column("nome", sa.String(length=80), nullable=False),
        sa.Column("tipo", sa.String(length=20), nullable=False),
        sa.Column("periodo", sa.String(length=20), nullable=False),
        sa.Column("valor_meta", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("ativa", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("data_criacao", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("tipo IN ('GANHO', 'DESPESA')", name="ck_metas_tipo"),
        sa.CheckConstraint("periodo IN ('SEMANAL', 'MENSAL')", name="ck_metas_periodo"),
        sa.CheckConstraint("valor_meta > 0", name="ck_metas_valor_meta_positivo"),
    )
    op.create_index("ix_metas_usuario_id", "metas", ["usuario_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_metas_usuario_id", table_name="metas")
    op.drop_table("metas")
