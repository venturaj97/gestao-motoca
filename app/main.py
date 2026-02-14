from fastapi import FastAPI

app = FastAPI()

@app.get("/saude")
def verificar_saude():
    return {"status": "ok"}
