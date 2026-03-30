import json
import re
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from sqlalchemy import func, select, distinct
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.abastecimento import Abastecimento
from app.models.lancamento import Lancamento
from app.models.manutencao import Manutencao
from app.models.moto_consulta_wdapi import MotoConsultaWDAPI
from app.models.moto_modelo import MotoModelo
from app.models.moto_usuario import MotoUsuario
from app.models.moto_versao import MotoVersao
from app.schemas.moto import (
    MotoUsuarioAtualizar,
    MotoUsuarioCriar,
    MotoUsuarioCriarPorPlaca,
)

PLACA_RE = re.compile(r"^[A-Z]{3}(?:[0-9]{4}|[0-9][A-Z][0-9]{2})$")


class ConsultaPlacaErro(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


def _parse_int(valor: Any) -> int | None:
    if valor is None:
        return None
    try:
        return int(str(valor).strip())
    except (TypeError, ValueError):
        return None


def listar_marcas(db: Session) -> list[str]:
    marcas = db.execute(
        select(distinct(MotoModelo.marca)).where(MotoModelo.ativo == True)  # noqa: E712
    ).scalars().all()
    return sorted(marcas)


def listar_modelos_por_marca(db: Session, marca: str) -> list[dict]:
    modelos = db.execute(
        select(MotoModelo)
        .where(MotoModelo.ativo == True)  # noqa: E712
        .where(MotoModelo.marca.ilike(marca))
        .order_by(MotoModelo.modelo)
    ).scalars().all()
    return [{"id": m.id, "marca": m.marca, "modelo": m.modelo, "cilindrada_cc": m.cilindrada_cc} for m in modelos]


def listar_anos_por_modelo(db: Session, modelo_id: int) -> list[dict]:
    versoes = db.execute(
        select(MotoVersao)
        .where(MotoVersao.moto_modelo_id == modelo_id)
        .where(MotoVersao.ativo == True)  # noqa: E712
        .order_by(MotoVersao.ano.desc())
    ).scalars().all()
    return [{"id": v.id, "ano": v.ano} for v in versoes]



def criar_moto_usuario(db: Session, dados: MotoUsuarioCriar) -> MotoUsuario:
    if dados.usuario_id is None:
        raise ValueError("usuario_obrigatorio")

    # valida se escolheu versao existente
    if dados.moto_versao_id:
        versao = db.execute(
            select(MotoVersao).where(MotoVersao.id == dados.moto_versao_id)
        ).scalar_one_or_none()

        if not versao:
            raise ValueError("versao_nao_encontrada")

    moto = MotoUsuario(
        usuario_id=dados.usuario_id,
        moto_versao_id=dados.moto_versao_id,
        marca_manual=dados.marca_manual,
        modelo_manual=dados.modelo_manual,
        ano_manual=dados.ano_manual,
        origem_dados="CATALOGO" if dados.moto_versao_id else "MANUAL",
        km_atual=dados.km_atual,
        cor=dados.cor,
        ativa=True,
    )

    db.add(moto)
    db.commit()
    db.refresh(moto)

    return moto


def alterar_ativa_moto_usuario(
    db: Session,
    usuario_id: int,
    moto_usuario_id: int,
    ativa: bool,
) -> MotoUsuario:
    moto = db.execute(
        select(MotoUsuario).where(
            MotoUsuario.id == moto_usuario_id,
            MotoUsuario.usuario_id == usuario_id,
        )
    ).scalar_one_or_none()
    if not moto:
        raise ValueError("moto_nao_encontrada_ou_nao_sua")

    moto.ativa = ativa
    db.commit()
    db.refresh(moto)
    return moto


def listar_motos_do_usuario(db: Session, usuario_id: int):
    stmt = (
        select(MotoUsuario, MotoVersao, MotoModelo)
        .outerjoin(MotoVersao, MotoUsuario.moto_versao_id == MotoVersao.id)
        .outerjoin(MotoModelo, MotoVersao.moto_modelo_id == MotoModelo.id)
        .where(MotoUsuario.usuario_id == usuario_id)
        .order_by(MotoUsuario.id.desc())
    )

    rows = db.execute(stmt).all()

    resultado = []
    for moto_usuario, versao, modelo in rows:
        if versao and modelo:
            resultado.append({
                "id": moto_usuario.id,
                "usuario_id": moto_usuario.usuario_id,
                "origem": "catalogo",
                "origem_dados": moto_usuario.origem_dados,
                "marca": modelo.marca,
                "modelo": modelo.modelo,
                "ano": versao.ano,
                "moto_versao_id": moto_usuario.moto_versao_id,
                "placa": moto_usuario.placa,
                "km_atual": moto_usuario.km_atual,
                "cor": moto_usuario.cor,
                "ativa": moto_usuario.ativa,
            })
        else:
            origem = "wdapi" if moto_usuario.origem_dados == "WDAPI" else "manual"
            resultado.append({
                "id": moto_usuario.id,
                "usuario_id": moto_usuario.usuario_id,
                "origem": origem,
                "origem_dados": moto_usuario.origem_dados,
                "marca": moto_usuario.marca_manual,
                "modelo": moto_usuario.modelo_manual,
                "ano": moto_usuario.ano_manual,
                "moto_versao_id": None,
                "placa": moto_usuario.placa,
                "km_atual": moto_usuario.km_atual,
                "cor": moto_usuario.cor,
                "ativa": moto_usuario.ativa,
            })

    return resultado


def atualizar_moto_usuario(
    db: Session,
    usuario_id: int,
    moto_usuario_id: int,
    dados: MotoUsuarioAtualizar,
) -> MotoUsuario:
    moto = db.execute(
        select(MotoUsuario).where(
            MotoUsuario.id == moto_usuario_id,
            MotoUsuario.usuario_id == usuario_id,
        )
    ).scalar_one_or_none()
    if not moto:
        raise ValueError("moto_nao_encontrada_ou_nao_sua")

    if dados.km_atual is not None:
        moto.km_atual = dados.km_atual
    if dados.cor is not None:
        moto.cor = dados.cor
    if dados.ativa is not None:
        moto.ativa = dados.ativa

    if moto.moto_versao_id is None:
        if dados.marca_manual is not None:
            moto.marca_manual = dados.marca_manual
        if dados.modelo_manual is not None:
            moto.modelo_manual = dados.modelo_manual
        if dados.ano_manual is not None:
            moto.ano_manual = dados.ano_manual

    db.commit()
    db.refresh(moto)
    return moto


def excluir_moto_usuario(db: Session, moto_usuario_id: int, usuario_id: int) -> None:
    moto = db.execute(
        select(MotoUsuario).where(
            MotoUsuario.id == moto_usuario_id,
            MotoUsuario.usuario_id == usuario_id,
        )
    ).scalar_one_or_none()
    if not moto:
        raise ValueError("moto_nao_encontrada_ou_nao_sua")

    n_lanc = db.execute(
        select(func.count())
        .select_from(Lancamento)
        .where(
            Lancamento.moto_usuario_id == moto_usuario_id,
            Lancamento.usuario_id == usuario_id,
        )
    ).scalar_one()
    n_abas = db.execute(
        select(func.count())
        .select_from(Abastecimento)
        .where(
            Abastecimento.moto_usuario_id == moto_usuario_id,
            Abastecimento.usuario_id == usuario_id,
        )
    ).scalar_one()
    n_manu = db.execute(
        select(func.count())
        .select_from(Manutencao)
        .where(
            Manutencao.moto_usuario_id == moto_usuario_id,
            Manutencao.usuario_id == usuario_id,
        )
    ).scalar_one()

    if n_lanc + n_abas + n_manu > 0:
        raise ValueError("moto_possui_registros")

    db.delete(moto)
    db.commit()


def _normalizar_placa(placa: str) -> str:
    placa_normalizada = placa.strip().upper().replace("-", "")
    if not PLACA_RE.match(placa_normalizada):
        raise ConsultaPlacaErro(401, "Placa Invalida favor usar o formato AAA0X00 ou AAA9999")
    return placa_normalizada


def _selecionar_melhor_fipe(payload: dict[str, Any]) -> dict[str, Any] | None:
    fipe = payload.get("fipe")
    if not isinstance(fipe, dict):
        return None

    dados_fipe = fipe.get("dados")
    if not isinstance(dados_fipe, list):
        return None

    candidatos = [item for item in dados_fipe if isinstance(item, dict)]
    if not candidatos:
        return None

    def _score(item: dict[str, Any]) -> int:
        try:
            return int(item.get("score", 0))
        except (TypeError, ValueError):
            return 0

    return max(candidatos, key=_score)


def _montar_resposta_consulta(placa_normalizada: str, payload: dict[str, Any]) -> dict[str, Any]:
    extra = payload.get("extra")
    melhor_fipe = _selecionar_melhor_fipe(payload)
    return {
        "placa_consultada": placa_normalizada,
        "extra_disponivel": isinstance(extra, dict) and len(extra) > 0,
        "fipe_disponivel": melhor_fipe is not None,
        "fipe_melhor_correspondencia": melhor_fipe,
        "dados": payload,
    }


def _salvar_cache_consulta_wdapi(
    db: Session,
    placa_normalizada: str,
    payload: dict[str, Any],
) -> None:
    melhor_fipe = _selecionar_melhor_fipe(payload)
    registro = db.execute(
        select(MotoConsultaWDAPI).where(MotoConsultaWDAPI.placa_consultada == placa_normalizada)
    ).scalar_one_or_none()

    if not registro:
        registro = MotoConsultaWDAPI(placa_consultada=placa_normalizada, dados_json=payload)
        db.add(registro)

    registro.marca = payload.get("marca") or payload.get("MARCA")
    registro.modelo = payload.get("modelo") or payload.get("MODELO")
    registro.ano_fabricacao = _parse_int(payload.get("ano"))
    registro.ano_modelo = _parse_int(payload.get("anoModelo"))
    registro.cor = payload.get("cor") or payload.get("COR")
    registro.municipio = payload.get("municipio")
    registro.uf = payload.get("uf")
    registro.situacao = payload.get("situacao")
    registro.origem = payload.get("origem")
    registro.fipe_melhor_score = _parse_int((melhor_fipe or {}).get("score"))
    registro.dados_json = payload
    registro.extra_json = payload.get("extra") if isinstance(payload.get("extra"), dict) else None
    registro.fipe_json = payload.get("fipe") if isinstance(payload.get("fipe"), dict) else None

    db.commit()


def consultar_dados_veiculo_por_placa(placa: str) -> dict[str, Any]:
    placa_normalizada = _normalizar_placa(placa)

    token = settings.wdapi_token.strip()
    if not token:
        raise ConsultaPlacaErro(402, "Token invalido")

    base_url = settings.wdapi_base_url.rstrip("/")
    url = f"{base_url}/{placa_normalizada}/{token}"
    request = Request(
        url=url,
        headers={
            "Accept": "application/json",
            "User-Agent": "gestao-motoca/1.0",
        },
    )

    try:
        with urlopen(request, timeout=settings.wdapi_timeout_segundos) as response:
            conteudo = response.read().decode("utf-8")
            payload = json.loads(conteudo)
    except HTTPError as e:
        detalhe_padrao = {
            400: "URL incorreta!",
            401: "Placa Invalida favor usar o formato AAA0X00 ou AAA9999",
            402: "Token invalido",
            406: "Sem resultados!",
            429: "Limite de consultas atingido!",
        }.get(e.code, "Falha ao consultar API externa de placa")

        detalhe = detalhe_padrao
        try:
            corpo = e.read().decode("utf-8")
            payload_erro = json.loads(corpo)
            if isinstance(payload_erro, dict) and isinstance(payload_erro.get("message"), str):
                detalhe = payload_erro["message"]
        except (UnicodeDecodeError, json.JSONDecodeError):
            pass

        if e.code in (400, 401, 402, 406, 429):
            raise ConsultaPlacaErro(e.code, detalhe)
        raise ConsultaPlacaErro(502, detalhe)
    except (URLError, TimeoutError, json.JSONDecodeError, UnicodeDecodeError):
        raise ConsultaPlacaErro(502, "Falha ao consultar API externa de placa")

    return _montar_resposta_consulta(placa_normalizada, payload)


def consultar_dados_veiculo_por_placa_com_cache(db: Session, placa: str) -> dict[str, Any]:
    placa_normalizada = _normalizar_placa(placa)
    cache = db.execute(
        select(MotoConsultaWDAPI).where(MotoConsultaWDAPI.placa_consultada == placa_normalizada)
    ).scalar_one_or_none()

    if cache:
        return _montar_resposta_consulta(placa_normalizada, cache.dados_json)

    resultado = consultar_dados_veiculo_por_placa(placa_normalizada)
    _salvar_cache_consulta_wdapi(db, placa_normalizada, resultado["dados"])
    return resultado


def criar_moto_usuario_por_placa(
    db: Session,
    usuario_id: int,
    dados: MotoUsuarioCriarPorPlaca,
) -> MotoUsuario:
    placa_normalizada = _normalizar_placa(dados.placa)

    ja_existe = db.execute(
        select(MotoUsuario).where(
            MotoUsuario.usuario_id == usuario_id,
            MotoUsuario.placa == placa_normalizada,
        )
    ).scalar_one_or_none()
    if ja_existe:
        raise ValueError("placa_ja_cadastrada_usuario")

    consulta = consultar_dados_veiculo_por_placa_com_cache(db, placa_normalizada)
    payload = consulta["dados"]

    marca = payload.get("marca") or payload.get("MARCA")
    modelo = payload.get("modelo") or payload.get("MODELO")
    ano_modelo = _parse_int(payload.get("anoModelo")) or _parse_int(payload.get("ano"))
    cor_api = payload.get("cor") or payload.get("COR")

    if not marca or not modelo:
        raise ValueError("dados_placa_incompletos")

    moto = MotoUsuario(
        usuario_id=usuario_id,
        moto_versao_id=None,
        marca_manual=str(marca).strip(),
        modelo_manual=str(modelo).strip(),
        ano_manual=ano_modelo,
        placa=placa_normalizada,
        origem_dados="WDAPI",
        km_atual=dados.km_atual,
        cor=dados.cor or cor_api,
        ativa=True,
    )

    db.add(moto)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("placa_ja_cadastrada_usuario")

    db.refresh(moto)
    return moto
