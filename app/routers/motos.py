from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, distinct

from app.database.session import get_db
from app.models.moto_modelo import MotoModelo
from app.models.moto_versao import MotoVersao

router = APIRouter(prefix="/motos", tags=["motos"])


@router.get("/marcas")
def listar_marcas(db: Session = Depends(get_db)):
    marcas = db.execute(
        select(distinct(MotoModelo.marca)).where(MotoModelo.ativo == True)  # noqa: E712
    ).scalars().all()
    return {"marcas": sorted(marcas)}


@router.get("/modelos")
def listar_modelos_por_marca(
    marca: str = Query(..., min_length=2),
    db: Session = Depends(get_db),
):
    modelos = db.execute(
        select(MotoModelo)
        .where(MotoModelo.ativo == True)  # noqa: E712
        .where(MotoModelo.marca.ilike(marca))
        .order_by(MotoModelo.modelo)
    ).scalars().all()

    return [{"id": m.id, "marca": m.marca, "modelo": m.modelo, "cilindrada_cc": m.cilindrada_cc} for m in modelos]


@router.get("/anos")
def listar_anos_por_modelo(
    modelo_id: int,
    db: Session = Depends(get_db),
):
    anos = db.execute(
        select(MotoVersao.ano)
        .where(MotoVersao.moto_modelo_id == modelo_id)
        .where(MotoVersao.ativo == True)  # noqa: E712
        .order_by(MotoVersao.ano.desc())
    ).scalars().all()

    return {"modelo_id": modelo_id, "anos": anos}