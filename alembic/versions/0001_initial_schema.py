"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-03-28 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "categorias",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=100), nullable=False),
        sa.Column("tipo", sa.String(length=20), nullable=False),
        sa.Column("ativo", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("data_criacao", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("tipo IN ('GANHO', 'DESPESA')", name="ck_categorias_tipo"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nome", "tipo", name="uq_categorias_nome_tipo"),
    )

    op.create_table(
        "motos_catalogo",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("marca", sa.String(length=80), nullable=False),
        sa.Column("modelo", sa.String(length=120), nullable=False),
        sa.Column("cilindrada_cc", sa.Integer(), nullable=True),
        sa.Column("tipo_combustivel", sa.String(length=30), nullable=True),
        sa.Column("consumo_medio_km_l", sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column("capacidade_tanque_l", sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column("ativo", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("data_criacao", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("marca", "modelo", name="uq_motos_catalogo_marca_modelo"),
    )

    op.create_table(
        "motos_consultas_wdapi",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("placa_consultada", sa.String(length=7), nullable=False),
        sa.Column("marca", sa.String(length=80), nullable=True),
        sa.Column("modelo", sa.String(length=120), nullable=True),
        sa.Column("ano_fabricacao", sa.Integer(), nullable=True),
        sa.Column("ano_modelo", sa.Integer(), nullable=True),
        sa.Column("cor", sa.String(length=40), nullable=True),
        sa.Column("municipio", sa.String(length=120), nullable=True),
        sa.Column("uf", sa.String(length=2), nullable=True),
        sa.Column("situacao", sa.String(length=120), nullable=True),
        sa.Column("origem", sa.String(length=40), nullable=True),
        sa.Column("fipe_melhor_score", sa.Integer(), nullable=True),
        sa.Column("dados_json", sa.JSON(), nullable=False),
        sa.Column("extra_json", sa.JSON(), nullable=True),
        sa.Column("fipe_json", sa.JSON(), nullable=True),
        sa.Column("consultado_em", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("placa_consultada", name="uq_motos_consultas_wdapi_placa"),
    )
    op.create_index("ix_motos_consultas_wdapi_placa_consultada", "motos_consultas_wdapi", ["placa_consultada"])

    op.create_table(
        "motos_modelos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("marca", sa.String(length=80), nullable=False),
        sa.Column("modelo", sa.String(length=120), nullable=False),
        sa.Column("cilindrada_cc", sa.Integer(), nullable=True),
        sa.Column("ativo", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("data_criacao", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("marca", "modelo", name="uq_motos_modelos_marca_modelo"),
    )

    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=180), nullable=False),
        sa.Column("senha", sa.String(length=255), nullable=False),
        sa.Column("data_criacao", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_usuarios_email", "usuarios", ["email"], unique=False)

    op.create_table(
        "motos_versoes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("moto_modelo_id", sa.Integer(), nullable=False),
        sa.Column("ano", sa.Integer(), nullable=False),
        sa.Column("tipo_combustivel", sa.String(length=30), nullable=True),
        sa.Column("consumo_medio_km_l", sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column("capacidade_tanque_l", sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column("ativo", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("data_criacao", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["moto_modelo_id"], ["motos_modelos.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("moto_modelo_id", "ano", name="uq_motos_versoes_modelo_ano"),
    )

    op.create_table(
        "motos_usuario",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("moto_versao_id", sa.Integer(), nullable=True),
        sa.Column("marca_manual", sa.String(length=80), nullable=True),
        sa.Column("modelo_manual", sa.String(length=120), nullable=True),
        sa.Column("ano_manual", sa.Integer(), nullable=True),
        sa.Column("placa", sa.String(length=7), nullable=True),
        sa.Column("origem_dados", sa.String(length=20), server_default=sa.text("'MANUAL'"), nullable=False),
        sa.Column("km_atual", sa.Integer(), nullable=False),
        sa.Column("cor", sa.String(length=40), nullable=True),
        sa.Column("ativa", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("data_cadastro", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "(moto_versao_id IS NOT NULL AND marca_manual IS NULL AND modelo_manual IS NULL) "
            "OR (moto_versao_id IS NULL AND marca_manual IS NOT NULL AND modelo_manual IS NOT NULL)",
            name="ck_origem_moto",
        ),
        sa.CheckConstraint("origem_dados IN ('MANUAL', 'CATALOGO', 'WDAPI')", name="ck_motos_usuario_origem_dados"),
        sa.ForeignKeyConstraint(["moto_versao_id"], ["motos_versoes.id"]),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("usuario_id", "placa", name="uq_motos_usuario_usuario_placa"),
    )
    op.create_index("ix_motos_usuario_placa", "motos_usuario", ["placa"], unique=False)

    op.create_table(
        "lancamentos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("moto_usuario_id", sa.Integer(), nullable=True),
        sa.Column("categoria_id", sa.Integer(), nullable=False),
        sa.Column("tipo", sa.String(length=20), nullable=False),
        sa.Column("valor", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("descricao", sa.String(length=255), nullable=True),
        sa.Column("data_lancamento", sa.Date(), server_default=sa.text("CURRENT_DATE"), nullable=False),
        sa.Column("data_criacao", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("tipo IN ('GANHO', 'DESPESA')", name="ck_lancamentos_tipo"),
        sa.CheckConstraint("valor > 0", name="ck_lancamentos_valor_positivo"),
        sa.ForeignKeyConstraint(["categoria_id"], ["categorias.id"]),
        sa.ForeignKeyConstraint(["moto_usuario_id"], ["motos_usuario.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "abastecimentos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("moto_usuario_id", sa.Integer(), nullable=True),
        sa.Column("lancamento_id", sa.Integer(), nullable=False),
        sa.Column("litros", sa.Numeric(precision=6, scale=2), nullable=False),
        sa.Column("valor_total", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("valor_litro", sa.Numeric(precision=8, scale=3), nullable=False),
        sa.Column("km_atual", sa.Integer(), nullable=True),
        sa.Column("data_abastecimento", sa.Date(), server_default=sa.text("CURRENT_DATE"), nullable=False),
        sa.Column("posto", sa.String(length=120), nullable=True),
        sa.Column("tipo_combustivel", sa.String(length=40), nullable=True),
        sa.Column("data_criacao", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("litros > 0", name="ck_abastecimentos_litros_positivos"),
        sa.CheckConstraint("valor_total > 0", name="ck_abastecimentos_valor_total_positivo"),
        sa.ForeignKeyConstraint(["lancamento_id"], ["lancamentos.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["moto_usuario_id"], ["motos_usuario.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("lancamento_id"),
    )

    op.create_table(
        "manutencoes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("moto_usuario_id", sa.Integer(), nullable=True),
        sa.Column("lancamento_id", sa.Integer(), nullable=False),
        sa.Column("valor_total", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("km_atual", sa.Integer(), nullable=True),
        sa.Column("data_manutencao", sa.Date(), server_default=sa.text("CURRENT_DATE"), nullable=False),
        sa.Column("descricao_servico", sa.String(length=255), nullable=True),
        sa.Column("oficina", sa.String(length=120), nullable=True),
        sa.Column("tipo_servico", sa.String(length=80), nullable=True),
        sa.Column("data_criacao", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("valor_total > 0", name="ck_manutencoes_valor_total_positivo"),
        sa.ForeignKeyConstraint(["lancamento_id"], ["lancamentos.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["moto_usuario_id"], ["motos_usuario.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("lancamento_id"),
    )


def downgrade() -> None:
    op.drop_table("manutencoes")
    op.drop_table("abastecimentos")
    op.drop_table("lancamentos")
    op.drop_index("ix_motos_usuario_placa", table_name="motos_usuario")
    op.drop_table("motos_usuario")
    op.drop_table("motos_versoes")
    op.drop_index("ix_usuarios_email", table_name="usuarios")
    op.drop_table("usuarios")
    op.drop_table("motos_modelos")
    op.drop_index("ix_motos_consultas_wdapi_placa_consultada", table_name="motos_consultas_wdapi")
    op.drop_table("motos_consultas_wdapi")
    op.drop_table("motos_catalogo")
    op.drop_table("categorias")
