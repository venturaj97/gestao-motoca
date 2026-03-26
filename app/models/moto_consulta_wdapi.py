from sqlalchemy import Column, DateTime, Integer, String, UniqueConstraint, func
from sqlalchemy.types import JSON

from app.database.base import Base


class MotoConsultaWDAPI(Base):
    __tablename__ = "motos_consultas_wdapi"
    __table_args__ = (
        UniqueConstraint("placa_consultada", name="uq_motos_consultas_wdapi_placa"),
    )

    id = Column(Integer, primary_key=True)
    placa_consultada = Column(String(7), nullable=False, index=True)

    marca = Column(String(80), nullable=True)
    modelo = Column(String(120), nullable=True)
    ano_fabricacao = Column(Integer, nullable=True)
    ano_modelo = Column(Integer, nullable=True)
    cor = Column(String(40), nullable=True)
    municipio = Column(String(120), nullable=True)
    uf = Column(String(2), nullable=True)
    situacao = Column(String(120), nullable=True)
    origem = Column(String(40), nullable=True)
    fipe_melhor_score = Column(Integer, nullable=True)

    dados_json = Column(JSON, nullable=False)
    extra_json = Column(JSON, nullable=True)
    fipe_json = Column(JSON, nullable=True)

    consultado_em = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    atualizado_em = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
