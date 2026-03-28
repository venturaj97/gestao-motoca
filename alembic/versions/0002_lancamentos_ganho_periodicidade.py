"""lancamentos ganho periodicidade

Revision ID: 0002_lancamentos_ganho_periodicidade
Revises: 0001_initial_schema
Create Date: 2026-03-28 00:00:01.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0002_lancamentos_ganho_periodicidade"
down_revision: Union[str, None] = "0001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("lancamentos", sa.Column("periodicidade_ganho", sa.String(length=20), nullable=True))
    op.add_column("lancamentos", sa.Column("minutos_corrida", sa.Integer(), nullable=True))
    op.add_column("lancamentos", sa.Column("km_corrida", sa.Numeric(precision=8, scale=2), nullable=True))

    op.create_check_constraint(
        "ck_lancamentos_periodicidade_ganho",
        "lancamentos",
        "periodicidade_ganho IS NULL OR periodicidade_ganho IN ('DIARIO', 'SEMANAL', 'CORRIDA')",
    )
    op.create_check_constraint(
        "ck_lancamentos_minutos_corrida_positivo",
        "lancamentos",
        "minutos_corrida IS NULL OR minutos_corrida > 0",
    )
    op.create_check_constraint(
        "ck_lancamentos_km_corrida_positivo",
        "lancamentos",
        "km_corrida IS NULL OR km_corrida > 0",
    )


def downgrade() -> None:
    op.drop_constraint("ck_lancamentos_km_corrida_positivo", "lancamentos", type_="check")
    op.drop_constraint("ck_lancamentos_minutos_corrida_positivo", "lancamentos", type_="check")
    op.drop_constraint("ck_lancamentos_periodicidade_ganho", "lancamentos", type_="check")

    op.drop_column("lancamentos", "km_corrida")
    op.drop_column("lancamentos", "minutos_corrida")
    op.drop_column("lancamentos", "periodicidade_ganho")
