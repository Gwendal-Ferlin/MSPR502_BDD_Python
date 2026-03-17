from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import auth, utilisateurs, sante, logs, reco, journal

app = FastAPI(
    title="HealthAI Coach API",
    description="API unique pour les microservices Utilisateur, Santé, Logs et Reco",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(utilisateurs.router, prefix="/api")
app.include_router(sante.router, prefix="/api")
app.include_router(journal.router, prefix="/api")
app.include_router(logs.router, prefix="/api")
app.include_router(reco.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "HealthAI Coach API", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}
