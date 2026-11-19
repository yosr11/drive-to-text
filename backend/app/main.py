
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import drive, batches


# ============================================================
# Initialisation de FastAPI
# ============================================================

app = FastAPI(
    title="Drive to Text API",
    description=(
        "API permettant de récupérer des fichiers depuis "
        "Google Drive et d'en extraire le texte "
        "à l'aide de PDF extraction et OCR."
    ),
    version="1.0.0"
)


# ============================================================
# Configuration CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ============================================================
# Enregistrement des routes
# ============================================================

app.include_router(drive.router)
app.include_router(batches.router)


# ============================================================
# Endpoint Health Check
# ============================================================

@app.get("/health", tags=["Health"])
def health_check():
    """
    Vérifie que l'API fonctionne correctement.
    """

    return {
        "status": "healthy",
        "message": "Drive to Text API is running."
    }
