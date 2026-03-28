"""lancamentos dia semana

Revision ID: 0003_lanc_dia_semana
Revises: 0002_lanc_ganho_periodo
Create Date: 2026-03-28 00:00:02.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0003_lanc_dia_semana"
down_revision: Union[str, None] = "0002_lanc_ganho_periodo"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("lancamentos", sa.Column("dia_semana", sa.String(length=20), nullable=True))

    op.execute(
        """
        UPDATE lancamentos
        SET dia_semana = CASE EXTRACT(DOW FROM data_lancamento)
            WHEN 0 THEN 'DOMINGO'
            WHEN 1 THEN 'SEGUNDA'
            WHEN 2 THEN 'TERCA'
            WHEN 3 THEN 'QUARTA'
            WHEN 4 THEN 'QUINTA'
            WHEN 5 THEN 'SEXTA'
            WHEN 6 THEN 'SABADO'
        END
        """
    )

    op.alter_column("lancamentos", "dia_semana", nullable=False)
    op.create_check_constraint(
        "ck_lancamentos_dia_semana",
        "lancamentos",
        "dia_semana IN ('SEGUNDA', 'TERCA', 'QUARTA', 'QUINTA', 'SEXTA', 'SABADO', 'DOMINGO')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_lancamentos_dia_semana", "lancamentos", type_="check")
    op.drop_column("lancamentos", "dia_semana")
