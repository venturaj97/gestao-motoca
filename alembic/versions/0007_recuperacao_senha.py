"""recuperacao de senha

Revision ID: 0007_recuperacao_senha
Revises: 0006_categorias_usuario_grupo
Create Date: 2026-08-19 00:00:07.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0007_recuperacao_senha"
down_revision: Union[str, None] = "0006_categorias_usuario_grupo"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "recuperacoes_senha",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("codigo_pin", sa.String(length=6), nullable=False),
        sa.Column("expira_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("usado", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("data_criacao", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_recuperacoes_senha_usuario_id", "recuperacoes_senha", ["usuario_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_recuperacoes_senha_usuario_id", table_name="recuperacoes_senha")
    op.drop_table("recuperacoes_senha")
