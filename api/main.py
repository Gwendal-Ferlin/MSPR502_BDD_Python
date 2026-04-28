from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from api.config import settings
from api.rate_limiting import limiter
from api.routers import auth, utilisateurs, sante, logs, reco, journal, gamification, ia_reco

app = FastAPI(
    title="HealthAI Coach API",
    description="API unique pour les microservices Utilisateur, Santé, Logs et Reco",
    version="1.0.0",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
if settings.rate_limit_enabled:
    app.add_middleware(SlowAPIMiddleware)

app.include_router(auth.router, prefix="/api")
app.include_router(utilisateurs.router, prefix="/api")
app.include_router(sante.router, prefix="/api")
app.include_router(journal.router, prefix="/api")
app.include_router(logs.router, prefix="/api")
app.include_router(reco.router, prefix="/api")
app.include_router(gamification.router, prefix="/api")
app.include_router(ia_reco.router, prefix="/api")


@app.get("/")
@limiter.exempt
def root():
    return {"message": "HealthAI Coach API", "docs": "/docs"}


@app.get("/health")
@limiter.exempt
def health():
    return {"status": "ok"}
