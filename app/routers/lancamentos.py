from datetime import date
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies import get_usuario_logado
from app.models.usuario import Usuario
from app.models.categoria import Categoria
from app.routers._errors import raise_mapped_error
from app.schemas.lancamento import (
    LancamentoCriar,
    LancamentoListaPaginadaResposta,
    LancamentoLoteCriar,
    LancamentoLoteItemResumo,
    LancamentoLoteResposta,
    LancamentoResposta,
)
from app.services.lancamento_service import (
    atualizar_lancamento,
    criar_lancamento,
    excluir_lancamento,
    listar_lancamentos,
)

router = APIRouter(prefix="/lancamentos", tags=["lancamentos"])


def _erros_lancamento_valor(e: ValueError) -> None:
    erros = {
        "tipo_invalido": (422, "Tipo deve ser GANHO ou DESPESA"),
        "categoria_nao_encontrada": (404, "Categoria nao encontrada"),
        "categoria_inativa": (422, "Categoria esta inativa"),
        "tipo_incompativel_com_categoria": (422, "Tipo do lancamento nao corresponde ao tipo da categoria"),
        "periodo_obrigatorio": (
            422,
            "Para lancamento de GANHO, informe periodo: DIARIO ou CORRIDA",
        ),
        "periodo_invalido": (422, "periodo invalido"),
        "data_lancamento_obrigatoria": (
            422,
            "Para lancamento de DESPESA, informe a data do lancamento",
        ),
        "dados_corrida_obrigatorios": (
            422,
            "Para GANHO por CORRIDA, informe minutos_corrida e km_corrida",
        ),
        "dados_corrida_nao_permitidos": (
            422,
            "minutos_corrida e km_corrida so podem ser informados quando periodo for CORRIDA",
        ),
        "campos_ganho_nao_permitidos_para_despesa": (
            422,
            "Campos de ganho nao sao permitidos quando tipo for DESPESA",
        ),
        "usuario_sem_moto": (422, "Cadastre uma moto antes de registrar"),
        "nenhuma_moto_ativa": (422, "Nenhuma moto ativa: ative uma moto ou informe qual moto no lancamento"),
        "moto_obrigatoria_informar": (422, "Informe qual moto (voce tem mais de uma moto ativa)"),
        "moto_nao_encontrada_ou_nao_sua": (404, "Moto nao encontrada ou nao pertence ao usuario"),
        "lancamento_nao_encontrado": (404, "Lancamento nao encontrado"),
        "lancamento_vinculado_apenas_despesa": (
            422,
            "Este lancamento esta vinculado a abastecimento ou manutencao: mantenha tipo DESPESA e categoria de despesa",
        ),
    }
    raise_mapped_error(e, erros)


@router.post("", response_model=LancamentoResposta, status_code=status.HTTP_201_CREATED)
def rota_criar_lancamento(
    dados: LancamentoCriar,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_logado),
):
    try:
        dados_com_usuario = dados.model_copy(update={"usuario_id": usuario.id})
        return criar_lancamento(db, dados_com_usuario)
    except ValueError as e:
        _erros_lancamento_valor(e)


@router.post("/lote", response_model=LancamentoLoteResposta, status_code=status.HTTP_201_CREATED)
def rota_criar_lancamentos_em_lote(
    dados: LancamentoLoteCriar,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_logado),
):
    criados = []
    primeiro_tipo: str | None = None
    primeira_data: date | None = None
    try:
        for item in dados.itens:
            item_usuario = item.model_copy(update={"usuario_id": usuario.id})
            lanc = criar_lancamento(db, item_usuario, auto_commit=False)
            criados.append(lanc)
            if primeiro_tipo is None:
                primeiro_tipo = lanc.tipo
            if primeira_data is None:
                primeira_data = lanc.data_lancamento

        db.commit()
        for lanc in criados:
            db.refresh(lanc)

        categorias_ids = {lanc.categoria_id for lanc in criados}
        categorias = db.query(Categoria).filter(Categoria.id.in_(categorias_ids)).all()
        nome_por_id = {c.id: c.nome for c in categorias}

        itens_resumo = [
            LancamentoLoteItemResumo(
                categoria_id=lanc.categoria_id,
                categoria_nome=nome_por_id.get(lanc.categoria_id, f"Categoria {lanc.categoria_id}"),
                valor=Decimal(lanc.valor),
            )
            for lanc in criados
        ]
        total_valor = sum((Decimal(lanc.valor) for lanc in criados), Decimal("0"))
        tipo_final = primeiro_tipo or "DESPESA"
        data_final = primeira_data or date.today()

        return LancamentoLoteResposta(
            quantidade=len(criados),
            tipo=tipo_final,
            data_lancamento=data_final,
            total_valor=total_valor,
            mensagem=f"{len(criados)} lancamento(s) registrado(s) com sucesso.",
            itens_resumo=itens_resumo,
            lancamentos=criados,
        )
    except ValueError as e:
        db.rollback()
        _erros_lancamento_valor(e)
    except Exception:
        db.rollback()
        raise


@router.put("/{lancamento_id}", response_model=LancamentoResposta)
def rota_atualizar_lancamento(
    lancamento_id: int,
    dados: LancamentoCriar,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_logado),
):
    try:
        dados_com_usuario = dados.model_copy(update={"usuario_id": usuario.id})
        return atualizar_lancamento(db, lancamento_id, dados_com_usuario)
    except ValueError as e:
        _erros_lancamento_valor(e)


@router.delete("/{lancamento_id}", status_code=status.HTTP_204_NO_CONTENT)
def rota_excluir_lancamento(
    lancamento_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_logado),
):
    try:
        excluir_lancamento(db, lancamento_id, usuario.id)
    except ValueError as e:
        _erros_lancamento_valor(e)


@router.get("", response_model=LancamentoListaPaginadaResposta)
def rota_listar_lancamentos(
    tipo: Optional[str] = Query(default=None),
    data_inicio: Optional[date] = Query(default=None),
    data_fim: Optional[date] = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_logado),
):
    itens, total = listar_lancamentos(
        db=db,
        usuario_id=usuario.id,
        tipo=tipo,
        data_inicio=data_inicio,
        data_fim=data_fim,
        pagina=pagina,
        limite=limite,
    )
    total_paginas = (total + limite - 1) // limite if total > 0 else 1
    return {
        "itens": itens,
        "total": total,
        "pagina": pagina,
        "limite": limite,
        "total_paginas": total_paginas,
    }
