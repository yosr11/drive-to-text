
from uuid import uuid4
from copy import deepcopy

from app.services.drive_service import download_file_content
from app.services.extraction_service import extract_file_text


# ============================================================
# Stockage temporaire des batches
# ============================================================

# Les batches sont conservés en mémoire pendant l'exécution
# de l'application.
BATCHES = {}


# ============================================================
# Création d'un batch
# ============================================================

def create_batch(files: list) -> dict:
    """
    Crée un batch et initialise tous ses fichiers
    avec le statut pending.

    Args:
        files: Liste des métadonnées des fichiers Google Drive.

    Returns:
        Informations du batch créé.
    """

    if not files:
        raise ValueError(
            "La liste des fichiers est vide."
        )

    batch_id = str(uuid4())

    results = []

    for file in files:

        file_id = file.get("id")
        filename = file.get("name", "unknown")
        mime_type = file.get("mimeType") or file.get("mime_type")

        if not file_id:
            raise ValueError(
                f"Identifiant manquant pour le fichier : {filename}"
            )

        results.append({
            "file_id": file_id,
            "filename": filename,
            "mime_type": mime_type,
            "status": "pending",
            "method": None,
            "text": None,
            "error": None
        })

    batch = {
        "batch_id": batch_id,
        "status": "pending",
        "total_files": len(results),
        "successful_files": 0,
        "failed_files": 0,
        "results": results
    }

    BATCHES[batch_id] = batch

    return deepcopy(batch)


# ============================================================
# Traitement individuel d'un fichier
# ============================================================

def process_single_file(file_result: dict, language: str = "eng") -> None:
    """
    Traite un seul fichier.

    Chaque fichier possède son propre bloc try/except
    afin qu'une erreur n'interrompe pas le batch.
    """

    file_result["status"] = "processing"

    try:

        # 1. Télécharger le fichier depuis Google Drive
        file_content = download_file_content(
            file_result["file_id"]
        )

        # 2. Extraire le texte selon le type MIME
        extraction_result = extract_file_text(
            file_content=file_content,
            mime_type=file_result["mime_type"],
            language=language
        )

        # 3. Enregistrer le résultat
        file_result["status"] = "done"
        file_result["method"] = extraction_result["method"]
        file_result["text"] = extraction_result["text"]
        file_result["error"] = None

    except Exception as exc:

        # Une erreur sur ce fichier ne bloque pas les autres.
        file_result["status"] = "failed"
        file_result["method"] = None
        file_result["text"] = None
        file_result["error"] = str(exc)


# ============================================================
# Traitement complet du batch
# ============================================================

def process_batch(
    batch_id: str,
    language: str = "eng"
) -> dict:
    """
    Traite tous les fichiers d'un batch.

    Chaque fichier est traité individuellement.
    Une erreur sur un fichier n'interrompt pas le traitement.

    Returns:
        Résultat complet du batch.
    """

    # 1. Vérifier l'existence du batch
    if batch_id not in BATCHES:
        raise ValueError(
            f"Batch introuvable : {batch_id}"
        )

    batch = BATCHES[batch_id]

    # 2. Passer le batch au statut processing
    batch["status"] = "processing"

    try:
        # 3. Traiter chaque fichier individuellement et publier les compteurs.
        for file_result in batch["results"]:

            process_single_file(
                file_result=file_result,
                language=language
            )

            batch["successful_files"] = sum(
                1 for file in batch["results"] if file["status"] == "done"
            )
            batch["failed_files"] = sum(
                1 for file in batch["results"] if file["status"] == "failed"
            )
    except Exception:
        batch["status"] = "failed"
        raise

    # 4. Le batch est terminé, même si certains fichiers ont échoué.
    batch["status"] = "done"

    return deepcopy(batch)


# ============================================================
# Récupération du résultat JSON
# ============================================================

def get_batch_result(batch_id: str) -> dict:
    """
    Construit et retourne le résultat JSON d'un batch.

    Le dictionnaire retourné est directement sérialisable
    en JSON par FastAPI.
    """

    if batch_id not in BATCHES:
        raise ValueError(
            f"Batch introuvable : {batch_id}"
        )

    batch = BATCHES[batch_id]

    return deepcopy({
        "batch_id": batch["batch_id"],
        "status": batch["status"],
        "total_files": batch["total_files"],
        "successful_files": batch["successful_files"],
        "failed_files": batch["failed_files"],
        "results": batch["results"]
    })
