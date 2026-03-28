from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.routers._errors import raise_mapped_error
from app.schemas.categoria import CategoriaResposta, CategoriaCriar
from app.services.categoria_service import listar_categorias, criar_categoria

router = APIRouter(prefix="/categorias", tags=["categorias"])


@router.get("", response_model=list[CategoriaResposta])
def rota_listar_categorias(db: Session = Depends(get_db)):
    return listar_categorias(db)


@router.post("", response_model=CategoriaResposta, status_code=status.HTTP_201_CREATED)
def rota_criar_categoria(dados: CategoriaCriar, db: Session = Depends(get_db)):
    try:
        return criar_categoria(db, dados)
    except ValueError as e:
        raise_mapped_error(
            e,
            {
                "tipo_invalido": (422, "Tipo deve ser GANHO ou DESPESA"),
                "categoria_ja_existe": (409, "Categoria ja existe"),
            },
        )
