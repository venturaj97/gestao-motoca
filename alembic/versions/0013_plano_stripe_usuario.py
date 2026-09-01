"""Campos de plano e Stripe no usuario

Revision ID: 0013
Revises: 0012
Create Date: 2026-08-31
"""

from alembic import op
import sqlalchemy as sa

revision = "0013_plano_stripe_usuario"
down_revision = "0012_tabela_cofres"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("usuarios", sa.Column("plano", sa.String(20), nullable=False, server_default="FREE"))
    op.add_column("usuarios", sa.Column("plano_expira_em", sa.DateTime(timezone=True), nullable=True))
    op.add_column("usuarios", sa.Column("stripe_customer_id", sa.String(100), nullable=True))
    op.add_column("usuarios", sa.Column("stripe_subscription_id", sa.String(100), nullable=True))


def downgrade() -> None:
    op.drop_column("usuarios", "stripe_subscription_id")
    op.drop_column("usuarios", "stripe_customer_id")
    op.drop_column("usuarios", "plano_expira_em")
    op.drop_column("usuarios", "plano")
