from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers.usuarios import router as usuarios_router
from app.routers.auth import router as auth_router
from app.routers.motos import router as motos_router
from app.routers.categorias import router as categorias_router
from app.routers.lancamentos import router as lancamentos_router
from app.routers.abastecimentos import router as abastecimentos_router
from app.routers.manutencoes import router as manutencoes_router
from app.routers.indicadores import router as indicadores_router
from app.routers.metas import router as metas_router
from app.routers.cofres import router as cofres_router
from app.routers.visao_mes import router as visao_mes_router
from app.routers.inteligencia import router as inteligencia_router
from app.routers.assinaturas import router as assinaturas_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        from app.database.base import Base
        from app.database.session import engine
        import app.models  # noqa: F401

        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Erro ao verificar tabelas: {e}")
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",          # Para quando você rodar o front local
        "https://gestaomoto.netlify.app", # Substitua pelo SEU link exato do Netlify
    ],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+|172\.\d+\.\d+\.\d+)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/saude")
def verificar_saude():
    return {"status": "ok"}

app.include_router(usuarios_router)
app.include_router(auth_router)
app.include_router(motos_router)
app.include_router(categorias_router)
app.include_router(lancamentos_router)
app.include_router(abastecimentos_router)
app.include_router(manutencoes_router)
app.include_router(indicadores_router)
app.include_router(metas_router)
app.include_router(cofres_router)
app.include_router(visao_mes_router)
app.include_router(inteligencia_router)
app.include_router(assinaturas_router)
