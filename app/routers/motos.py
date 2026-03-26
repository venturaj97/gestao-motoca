from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.moto import (
    ConsultaPlacaResposta,
    MotoUsuarioAtivaAlterar,
    MotoUsuarioAtualizar,
    MotoUsuarioCriar,
    MotoUsuarioResposta,
)
from app.services.moto_service import (
    ConsultaPlacaErro,
    consultar_dados_veiculo_por_placa,
    listar_marcas,
    listar_modelos_por_marca,
    listar_anos_por_modelo,
    alterar_ativa_moto_usuario,
    atualizar_moto_usuario,
    criar_moto_usuario,
    excluir_moto_usuario,
    listar_motos_do_usuario,
)

router = APIRouter(prefix="/motos", tags=["motos"])


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
def rota_consultar_veiculo_por_placa(placa: str):
    try:
        return consultar_dados_veiculo_por_placa(placa)
    except ConsultaPlacaErro as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.post("/minha", response_model=MotoUsuarioResposta, status_code=status.HTTP_201_CREATED)
def rota_cadastrar_minha_moto(dados: MotoUsuarioCriar, db: Session = Depends(get_db)):
    try:
        return criar_moto_usuario(db, dados)
    except ValueError as e:
        if str(e) == "versao_nao_encontrada":
            raise HTTPException(status_code=404, detail="Versao nao encontrada")
        raise


@router.patch("/minha/ativa", response_model=MotoUsuarioResposta)
def rota_alterar_ativa_moto(dados: MotoUsuarioAtivaAlterar, db: Session = Depends(get_db)):
    try:
        return alterar_ativa_moto_usuario(db, dados)
    except ValueError as e:
        if str(e) == "moto_nao_encontrada_ou_nao_sua":
            raise HTTPException(status_code=404, detail="Moto nao encontrada ou nao pertence ao usuario")
        raise HTTPException(status_code=400, detail="Erro desconhecido")


@router.put("/minha/{moto_usuario_id}", response_model=MotoUsuarioResposta)
def rota_atualizar_minha_moto(
    moto_usuario_id: int,
    dados: MotoUsuarioAtualizar,
    db: Session = Depends(get_db),
):
    try:
        return atualizar_moto_usuario(db, moto_usuario_id, dados)
    except ValueError as e:
        if str(e) == "moto_nao_encontrada_ou_nao_sua":
            raise HTTPException(status_code=404, detail="Moto nao encontrada ou nao pertence ao usuario")
        raise HTTPException(status_code=400, detail="Erro desconhecido")


@router.delete("/minha/{moto_usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def rota_excluir_minha_moto(
    moto_usuario_id: int,
    usuario_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
):
    try:
        excluir_moto_usuario(db, moto_usuario_id, usuario_id)
    except ValueError as e:
        if str(e) == "moto_nao_encontrada_ou_nao_sua":
            raise HTTPException(status_code=404, detail="Moto nao encontrada ou nao pertence ao usuario")
        if str(e) == "moto_possui_registros":
            raise HTTPException(
                status_code=409,
                detail="Nao e possivel excluir: existem lancamentos, abastecimentos ou manutencoes nesta moto",
            )
        raise HTTPException(status_code=400, detail="Erro desconhecido")


@router.get("/minha")
def rota_listar_minhas_motos(
    usuario_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
):
    return {"usuario_id": usuario_id, "motos": listar_motos_do_usuario(db, usuario_id)}
