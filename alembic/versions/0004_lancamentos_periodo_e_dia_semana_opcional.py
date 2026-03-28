"""renomeia periodicidade para periodo e ajusta dia_semana

Revision ID: 0004_lanc_periodo_diasem
Revises: 0003_lanc_dia_semana
Create Date: 2026-03-28 00:00:03.000000
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "0004_lanc_periodo_diasem"
down_revision: Union[str, None] = "0003_lanc_dia_semana"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("ck_lancamentos_periodicidade_ganho", "lancamentos", type_="check")
    op.alter_column("lancamentos", "periodicidade_ganho", new_column_name="periodo")
    op.create_check_constraint(
        "ck_lancamentos_periodo",
        "lancamentos",
        "periodo IS NULL OR periodo IN ('DIARIO', 'SEMANAL', 'CORRIDA')",
    )

    op.execute(
        """
        UPDATE lancamentos
        SET dia_semana = NULL
        WHERE tipo = 'GANHO' AND periodo = 'SEMANAL'
        """
    )
    op.alter_column("lancamentos", "dia_semana", nullable=True)


def downgrade() -> None:
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
        WHERE dia_semana IS NULL
        """
    )
    op.alter_column("lancamentos", "dia_semana", nullable=False)

    op.drop_constraint("ck_lancamentos_periodo", "lancamentos", type_="check")
    op.alter_column("lancamentos", "periodo", new_column_name="periodicidade_ganho")
    op.create_check_constraint(
        "ck_lancamentos_periodicidade_ganho",
        "lancamentos",
        "periodicidade_ganho IS NULL OR periodicidade_ganho IN ('DIARIO', 'SEMANAL', 'CORRIDA')",
    )
