from datetime import date

from fastapi import APIRouter, Depends, Query
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies import get_usuario_logado
from app.models.usuario import Usuario
from app.schemas.inteligencia import InteligenciaResumo
from app.services.inteligencia_service import obter_inteligencia_resumo

router = APIRouter(prefix="/inteligencia", tags=["inteligencia"])


@router.get("/resumo", response_model=InteligenciaResumo)
def rota_inteligencia_resumo(
    ano: int = Query(default=None, ge=2000, le=2100),
    mes: int = Query(default=None, ge=1, le=12),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_logado),
):
    hoje = date.today()
    return obter_inteligencia_resumo(
        db=db,
        usuario_id=usuario.id,
        ano=ano or hoje.year,
        mes=mes or hoje.month,
    )
