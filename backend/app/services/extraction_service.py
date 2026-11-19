
from app.services.pdf_service import (
    extract_pdf_text_with_ocr,
    PDFExtractionError
)

from app.services.ocr_service import (
    extract_image_text,
    OCRExtractionError
)


# ============================================================
# Types MIME supportés
# ============================================================

SUPPORTED_MIME_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg"
}


# ============================================================
# Exceptions
# ============================================================

class FileExtractionError(Exception):
    """Erreur générale pendant l'extraction d'un fichier."""
    pass


class UnsupportedFileTypeError(FileExtractionError):
    """Type de fichier non supporté."""
    pass


# ============================================================
# Service central d'extraction
# ============================================================

def extract_file_text(
    file_content: bytes,
    mime_type: str,
    language: str = "eng"
) -> dict:
    """
    Choisit automatiquement le service d'extraction
    selon le type MIME du fichier.

    Args:
        file_content: Contenu binaire du fichier.
        mime_type: Type MIME (PDF, PNG ou JPEG).
        language: Langue utilisée pour l'OCR.

    Returns:
        Un dictionnaire contenant :
        - method : méthode d'extraction utilisée.
        - text : texte extrait.

    Raises:
        UnsupportedFileTypeError: Type de fichier non supporté.
        FileExtractionError: Erreur pendant l'extraction.
    """

    # 1. Vérifier le contenu du fichier
    if not file_content:
        raise FileExtractionError(
            "Le contenu du fichier est vide."
        )

    # 2. Vérifier le type MIME
    if mime_type not in SUPPORTED_MIME_TYPES:
        raise UnsupportedFileTypeError(
            f"Type de fichier non supporté : {mime_type}"
        )

    try:

        # 3. Traitement des fichiers PDF
        if mime_type == "application/pdf":

            result = extract_pdf_text_with_ocr(
                file_content,
                language=language
            )

        # 4. Traitement des images
        elif mime_type in ("image/png", "image/jpeg"):

            result = extract_image_text(
                file_content,
                language=language
            )

        else:
            raise UnsupportedFileTypeError(
                f"Type de fichier non supporté : {mime_type}"
            )

        # 5. Retourner le résultat
        return {
            "method": result["method"],
            "text": result["text"]
        }

    except (PDFExtractionError, OCRExtractionError):
        raise

    except FileExtractionError:
        raise

    except Exception as exc:
        raise FileExtractionError(
            f"Erreur pendant l'extraction du fichier : {exc}"
        ) from exc
