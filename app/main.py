from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.usuarios import router as usuarios_router
from app.routers.auth import router as auth_router
from app.routers.motos import router as motos_router
from app.routers.categorias import router as categorias_router
from app.routers.lancamentos import router as lancamentos_router
from app.routers.abastecimentos import router as abastecimentos_router
from app.routers.manutencoes import router as manutencoes_router
from app.routers.indicadores import router as indicadores_router
from app.routers.metas import router as metas_router
from app.routers.visao_mes import router as visao_mes_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # schema passa a ser controlado por Alembic (migrations)
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
        "http://localhost:4173",
    ],
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
app.include_router(visao_mes_router)
