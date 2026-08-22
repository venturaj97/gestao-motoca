"""motos historico km

Revision ID: 0010_motos_historico_km
Revises: 0009_padronizacao_audit_mixin
Create Date: 2026-08-22 00:00:10.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0010_motos_historico_km"
down_revision: Union[str, None] = "0009_padronizacao_audit_mixin"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "motos_historico_km",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False),
        sa.Column("moto_usuario_id", sa.Integer(), sa.ForeignKey("motos_usuario.id", ondelete="CASCADE"), nullable=False),
        sa.Column("km", sa.Integer(), nullable=False),
        sa.Column("origem", sa.String(30), nullable=False, server_default="ATUALIZACAO_RAPIDA"),
        sa.Column("situacao", sa.String(20), nullable=False, server_default="ATIVO"),
        sa.Column("data", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("data_criacao", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_motos_historico_km_usuario_moto", "motos_historico_km", ["usuario_id", "moto_usuario_id"])


def downgrade() -> None:
    op.drop_index("ix_motos_historico_km_usuario_moto", table_name="motos_historico_km")
    op.drop_table("motos_historico_km")
