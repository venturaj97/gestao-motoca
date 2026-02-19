from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database.session import get_db
from app.models.moto_catalogo import MotoCatalogo

router = APIRouter(prefix="/motos", tags=["motos"])


@router.get("/catalogo")
def listar_motos_catalogo(db: Session = Depends(get_db)):
    motos = db.execute(
        select(MotoCatalogo).where(MotoCatalogo.ativo == True)  # noqa: E712
    ).scalars().all()

    return [
        {
            "id": m.id,
            "marca": m.marca,
            "modelo": m.modelo,
            "cilindrada_cc": m.cilindrada_cc,
            "tipo_combustivel": m.tipo_combustivel,
            "consumo_medio_km_l": float(m.consumo_medio_km_l) if m.consumo_medio_km_l is not None else None,
            "capacidade_tanque_l": float(m.capacidade_tanque_l) if m.capacidade_tanque_l is not None else None,
        }
        for m in motos
    ]
