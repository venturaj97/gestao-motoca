from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.database.base import Base
from app.database.session import engine

from app.routers.usuarios import router as usuarios_router
from app.routers.motos import router as motos_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # garante que os models foram importados (registrados no Base)
    from app.models.usuario import Usuario  # noqa: F401
    from app.models.moto_catalogo import MotoCatalogo  # noqa: F401
    from app.models.moto_usuario import MotoUsuario  # noqa: F401

    Base.metadata.create_all(bind=engine)
    yield
    # aqui entraria shutdown, se precisar

app = FastAPI(lifespan=lifespan)

@app.get("/saude")
def verificar_saude():
    return {"status": "ok"}

app.include_router(usuarios_router)
app.include_router(motos_router)
