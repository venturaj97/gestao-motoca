"""categorias por usuario e grupo de despesa

Revision ID: 0006_categorias_usuario_grupo
Revises: 0005_metas_usuario
Create Date: 2026-04-03 00:00:05.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0006_categorias_usuario_grupo"
down_revision: Union[str, None] = "0005_metas_usuario"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("categorias", sa.Column("usuario_id", sa.Integer(), nullable=True))
    op.add_column("categorias", sa.Column("grupo_despesa", sa.String(length=20), nullable=True))

    op.create_foreign_key(
        "fk_categorias_usuario_id_usuarios",
        "categorias",
        "usuarios",
        ["usuario_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index("ix_categorias_usuario_id", "categorias", ["usuario_id"], unique=False)

    op.drop_constraint("uq_categorias_nome_tipo", "categorias", type_="unique")
    op.create_unique_constraint(
        "uq_categorias_usuario_nome_tipo",
        "categorias",
        ["usuario_id", "nome", "tipo"],
    )

    op.create_check_constraint(
        "ck_categorias_grupo_despesa",
        "categorias",
        "grupo_despesa IS NULL OR grupo_despesa IN ('GERAL', 'MANUTENCAO', 'ABASTECIMENTO', 'IMPOSTO')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_categorias_grupo_despesa", "categorias", type_="check")

    op.drop_constraint("uq_categorias_usuario_nome_tipo", "categorias", type_="unique")
    op.create_unique_constraint("uq_categorias_nome_tipo", "categorias", ["nome", "tipo"])

    op.drop_index("ix_categorias_usuario_id", table_name="categorias")
    op.drop_constraint("fk_categorias_usuario_id_usuarios", "categorias", type_="foreignkey")

    op.drop_column("categorias", "grupo_despesa")
    op.drop_column("categorias", "usuario_id")
