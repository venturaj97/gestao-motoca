"""adiciona suporte a dias de trabalho por semana e cofres em metas

Revision ID: 0011_metas_dias_trabalho_cofres
Revises: 0010_motos_historico_km
Create Date: 2026-08-25 00:00:11.000000
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = "0011_metas_dias_trabalho_cofres"
down_revision: Union[str, None] = "0010_motos_historico_km"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "metas",
        sa.Column("dias_trabalho_semana", sa.Integer(), nullable=True, server_default="6"),
    )
    op.add_column(
        "metas",
        sa.Column("categoria_cofre", sa.String(length=50), nullable=True),
    )

    # Atualiza a constraint do periodo
    op.drop_constraint("ck_metas_periodo", "metas", type_="check")
    op.create_check_constraint(
        "ck_metas_periodo",
        "metas",
        "periodo IN ('DIARIO', 'SEMANAL', 'MENSAL', 'OBJETIVO')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_metas_periodo", "metas", type_="check")
    op.create_check_constraint(
        "ck_metas_periodo",
        "metas",
        "periodo IN ('SEMANAL', 'MENSAL')",
    )
    op.drop_column("metas", "categoria_cofre")
    op.drop_column("metas", "dias_trabalho_semana")
