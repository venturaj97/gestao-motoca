from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies import get_usuario_logado
from app.models.usuario import Usuario
from app.routers._errors import raise_mapped_error
from app.schemas.moto import (
    ConsultaPlacaResposta,
    MotoUsuarioAtivaAlterar,
    MotoUsuarioAtualizar,
    MotoUsuarioCriar,
    MotoUsuarioCriarPorPlaca,
    MotoUsuarioResposta,
)
from app.services.moto_service import (
    ConsultaPlacaErro,
    consultar_dados_veiculo_por_placa_com_cache,
    listar_marcas,
    listar_modelos_por_marca,
    listar_anos_por_modelo,
    alterar_ativa_moto_usuario,
    atualizar_moto_usuario,
    criar_moto_usuario,
    criar_moto_usuario_por_placa,
    excluir_moto_usuario,
    listar_motos_do_usuario,
)

router = APIRouter(prefix="/motos", tags=["motos"])

ERROS_MOTO = {
    "versao_nao_encontrada": (404, "Versao nao encontrada"),
    "placa_ja_cadastrada_usuario": (409, "Placa ja cadastrada para este usuario"),
    "dados_placa_incompletos": (422, "Dados insuficientes retornados para cadastrar a moto"),
    "moto_nao_encontrada_ou_nao_sua": (404, "Moto nao encontrada ou nao pertence ao usuario"),
    "moto_possui_registros": (
        409,
        "Nao e possivel excluir: existem lancamentos, abastecimentos ou manutencoes nesta moto",
    ),
}


@router.get("/marcas")
def rota_listar_marcas(db: Session = Depends(get_db)):
    return {"marcas": listar_marcas(db)}


@router.get("/modelos")
def rota_listar_modelos_por_marca(
    marca: str = Query(..., min_length=2),
    db: Session = Depends(get_db),
):
    return listar_modelos_por_marca(db, marca)


@router.get("/anos")
def rota_listar_anos_por_modelo(
    modelo_id: int,
    db: Session = Depends(get_db),
):
    return {"modelo_id": modelo_id, "anos": listar_anos_por_modelo(db, modelo_id)}


@router.get("/consulta-placa/{placa}", response_model=ConsultaPlacaResposta)
def rota_consultar_veiculo_por_placa(
    placa: str,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_logado),
):
    _ = usuario
    try:
        return consultar_dados_veiculo_por_placa_com_cache(db, placa)
    except ConsultaPlacaErro as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.post("/minha", response_model=MotoUsuarioResposta, status_code=status.HTTP_201_CREATED)
def rota_cadastrar_minha_moto(
    dados: MotoUsuarioCriar,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_logado),
):
    try:
        dados_com_usuario = dados.model_copy(update={"usuario_id": usuario.id})
        return criar_moto_usuario(db, dados_com_usuario)
    except ValueError as e:
        raise_mapped_error(e, ERROS_MOTO)


@router.post("/minha/placa", response_model=MotoUsuarioResposta, status_code=status.HTTP_201_CREATED)
def rota_cadastrar_minha_moto_por_placa(
    dados: MotoUsuarioCriarPorPlaca,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_logado),
):
    try:
        return criar_moto_usuario_por_placa(db, usuario.id, dados)
    except ConsultaPlacaErro as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ValueError as e:
        raise_mapped_error(e, ERROS_MOTO)


@router.patch("/minha/ativa", response_model=MotoUsuarioResposta)
def rota_alterar_ativa_moto(
    dados: MotoUsuarioAtivaAlterar,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_logado),
):
    try:
        return alterar_ativa_moto_usuario(db, usuario.id, dados.moto_usuario_id, dados.ativa)
    except ValueError as e:
        raise_mapped_error(e, ERROS_MOTO)


@router.put("/minha/{moto_usuario_id}", response_model=MotoUsuarioResposta)
def rota_atualizar_minha_moto(
    moto_usuario_id: int,
    dados: MotoUsuarioAtualizar,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_logado),
):
    try:
        return atualizar_moto_usuario(db, usuario.id, moto_usuario_id, dados)
    except ValueError as e:
        raise_mapped_error(e, ERROS_MOTO)


@router.delete("/minha/{moto_usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def rota_excluir_minha_moto(
    moto_usuario_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_logado),
):
    try:
        excluir_moto_usuario(db, moto_usuario_id, usuario.id)
    except ValueError as e:
        raise_mapped_error(e, ERROS_MOTO)


@router.get("/minha")
def rota_listar_minhas_motos(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_logado),
):
    return {"usuario_id": usuario.id, "motos": listar_motos_do_usuario(db, usuario.id)}
