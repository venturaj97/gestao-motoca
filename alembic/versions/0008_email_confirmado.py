"""email confirmado

Revision ID: 0008_email_confirmado
Revises: 0007_recuperacao_senha
Create Date: 2026-08-19 00:00:08.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0008_email_confirmado"
down_revision: Union[str, None] = "0007_recuperacao_senha"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = [col["name"] for col in inspector.get_columns("usuarios")]
    if "email_confirmado" not in columns:
        op.add_column(
            "usuarios",
            sa.Column("email_confirmado", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        )


def downgrade() -> None:
    op.drop_column("usuarios", "email_confirmado")
