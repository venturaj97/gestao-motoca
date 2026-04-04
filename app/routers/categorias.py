from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies import get_usuario_logado
from app.models.usuario import Usuario
from app.routers._errors import raise_mapped_error
from app.schemas.categoria import CategoriaResposta, CategoriaCriar, CategoriaAtualizar
from app.services.categoria_service import (
    listar_categorias,
    criar_categoria,
    atualizar_categoria,
    excluir_categoria,
)

router = APIRouter(prefix="/categorias", tags=["categorias"])


@router.get("", response_model=list[CategoriaResposta])
def rota_listar_categorias(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_logado),
):
    return listar_categorias(db, usuario.id)


@router.post("", response_model=CategoriaResposta, status_code=status.HTTP_201_CREATED)
def rota_criar_categoria(
    dados: CategoriaCriar,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_logado),
):
    try:
        return criar_categoria(db, usuario.id, dados)
    except ValueError as e:
        raise_mapped_error(
            e,
            {
                "tipo_invalido": (422, "Tipo deve ser GANHO ou DESPESA"),
                "grupo_despesa_obrigatorio": (
                    422,
                    "Para categoria de despesa, informe grupo_despesa: GERAL, MANUTENCAO, ABASTECIMENTO ou IMPOSTO",
                ),
                "grupo_despesa_invalido": (
                    422,
                    "grupo_despesa invalido. Use: GERAL, MANUTENCAO, ABASTECIMENTO ou IMPOSTO",
                ),
                "grupo_despesa_nao_permitido_para_ganho": (
                    422,
                    "grupo_despesa so pode ser usado em categoria de DESPESA",
                ),
                "categoria_ja_existe": (409, "Categoria ja existe"),
            },
        )


@router.put("/{categoria_id}", response_model=CategoriaResposta)
def rota_atualizar_categoria(
    categoria_id: int,
    dados: CategoriaAtualizar,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_logado),
):
    try:
        return atualizar_categoria(db, usuario.id, categoria_id, dados)
    except ValueError as e:
        raise_mapped_error(
            e,
            {
                "categoria_nao_encontrada": (404, "Categoria nao encontrada"),
                "nome_obrigatorio": (422, "Informe um nome valido"),
                "grupo_despesa_obrigatorio": (
                    422,
                    "Para categoria de despesa, informe grupo_despesa: GERAL, MANUTENCAO, ABASTECIMENTO ou IMPOSTO",
                ),
                "grupo_despesa_invalido": (
                    422,
                    "grupo_despesa invalido. Use: GERAL, MANUTENCAO, ABASTECIMENTO ou IMPOSTO",
                ),
                "grupo_despesa_nao_permitido_para_ganho": (
                    422,
                    "grupo_despesa so pode ser usado em categoria de DESPESA",
                ),
                "categoria_ja_existe": (409, "Categoria ja existe"),
            },
        )


@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def rota_excluir_categoria(
    categoria_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_logado),
):
    try:
        excluir_categoria(db, usuario.id, categoria_id)
    except ValueError as e:
        raise_mapped_error(
            e,
            {
                "categoria_nao_encontrada": (404, "Categoria nao encontrada"),
            },
        )
