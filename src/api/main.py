from fastapi import FastAPI
from src.api.routes import router
from src.engine.w2v_loader import W2VLoader

app = FastAPI(
    title="descrEVE API",
    description="API de NLP para monitoramento de queimadas",
    version="2.0.0"
)


app.include_router(router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    print(" Inicializando aplicação...")

    # Força a instanciação do Loader.
    # Isso vai disparar o _load_model() e carregar o arquivo cbow_s300.txt na RAM.
    W2VLoader()

    print("Aplicação pronta para receber requisições!")


@app.get("/")
def read_root():
    return {"status": "online", "project": "descrEVE v2"}
