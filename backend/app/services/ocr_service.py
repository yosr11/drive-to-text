
import os
import shutil
from pathlib import Path
from io import BytesIO

import pytesseract
from PIL import Image, UnidentifiedImageError


# Configuration de Tesseract

TESSERACT_DEFAULT_PATH = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

# Utiliser le chemin défini dans les variables d'environnement
# ou détecter automatiquement Tesseract.
TESSERACT_PATH = os.getenv("TESSERACT_CMD")

if TESSERACT_PATH and Path(TESSERACT_PATH).is_file():
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

elif Path(TESSERACT_DEFAULT_PATH).is_file():
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_DEFAULT_PATH

elif shutil.which("tesseract"):
    pytesseract.pytesseract.tesseract_cmd = shutil.which("tesseract")


# Langues prises en charge par notre application
SUPPORTED_LANGUAGES = {
    "eng",
    "fra",
    "ara",
    "eng+fra",
    "eng+ara",
    "fra+ara",
    "eng+fra+ara",
}


# Exceptions personnalisées

class OCRExtractionError(Exception):
    """Erreur générale lors de l'extraction OCR."""
    pass


class InvalidImageError(OCRExtractionError):
    """Image invalide ou illisible."""
    pass


class EmptyImageError(OCRExtractionError):
    """Image vide."""
    pass


class OCRLanguageError(OCRExtractionError):
    """Langue OCR invalide ou non installée."""
    pass


class TesseractNotAvailableError(OCRExtractionError):
    """Tesseract est introuvable ou inaccessible."""
    pass


def open_image(image_source) -> Image.Image:
    """
    Ouvre une image depuis un chemin local ou des données en mémoire.

    Args:
        image_source:
            - str ou Path : chemin local de l'image.
            - bytes : contenu binaire de l'image.
            - BytesIO : flux de données en mémoire.
            - PIL.Image.Image : image déjà ouverte.

    Returns:
        Une image Pillow chargée et convertie en RGB.
    """

    try:

        # Cas 1 : image déjà ouverte avec Pillow
        if isinstance(image_source, Image.Image):
            image = image_source.copy()

        # Cas 2 : image reçue sous forme de bytes
        elif isinstance(image_source, bytes):

            if not image_source:
                raise EmptyImageError(
                    "Le contenu de l'image est vide."
                )

            image = Image.open(BytesIO(image_source))
            image.load()

        # Cas 3 : image reçue sous forme de BytesIO
        elif isinstance(image_source, BytesIO):

            if image_source.getbuffer().nbytes == 0:
                raise EmptyImageError(
                    "Le contenu de l'image est vide."
                )

            image_source.seek(0)
            image = Image.open(image_source)
            image.load()

        # Cas 4 : image reçue depuis un chemin local
        elif isinstance(image_source, (str, Path)):

            path = Path(image_source)

            if not path.exists() or not path.is_file():
                raise FileNotFoundError(
                    f"Image introuvable : {image_source}"
                )

            if path.stat().st_size == 0:
                raise EmptyImageError(
                    "Le fichier image est vide."
                )

            with Image.open(path) as opened_image:
                opened_image.load()
                image = opened_image.copy()

        else:
            raise TypeError(
                "Source image invalide. Fournissez un chemin local, "
                "des bytes, un BytesIO ou une image Pillow."
            )

        # Vérifier les dimensions
        if image.width == 0 or image.height == 0:
            raise EmptyImageError(
                "L'image ne possède aucune dimension valide."
            )

        # Convertir l'image en RGB pour faciliter le traitement OCR
        return image.convert("RGB")

    except OCRExtractionError:
        raise

    except FileNotFoundError:
        raise

    except UnidentifiedImageError as exc:
        raise InvalidImageError(
            "Le fichier fourni n'est pas une image valide."
        ) from exc

    except (OSError, ValueError) as exc:
        raise InvalidImageError(
            f"Impossible d'ouvrir l'image : {exc}"
        ) from exc


def validate_language(language: str) -> None:
    """
    Vérifie que la langue demandée est prise en charge
    par notre application.
    """

    if not isinstance(language, str) or language not in SUPPORTED_LANGUAGES:
        raise OCRLanguageError(
            f"Langue non prise en charge : {language}. "
            f"Langues acceptées : {', '.join(sorted(SUPPORTED_LANGUAGES))}"
        )


def extract_text_from_image(
    image: Image.Image,
    language: str = "eng"
) -> str:
    """
    Applique Tesseract OCR sur une image Pillow.

    Args:
        image: Image déjà ouverte avec Pillow.
        language: Langue ou combinaison de langues.

    Returns:
        Texte reconnu par Tesseract.
    """

    validate_language(language)

    try:
        text = pytesseract.image_to_string(
            image,
            lang=language
        )

        return text.strip()

    except pytesseract.pytesseract.TesseractNotFoundError as exc:
        raise TesseractNotAvailableError(
            "Tesseract est introuvable. Vérifiez son installation "
            "et son chemin d'accès."
        ) from exc

    except pytesseract.pytesseract.TesseractError as exc:
        raise OCRLanguageError(
            f"Erreur Tesseract. Vérifiez que la langue '{language}' "
            f"est installée. Détail : {exc}"
        ) from exc

    except Exception as exc:
        raise OCRExtractionError(
            f"Erreur pendant l'extraction OCR : {exc}"
        ) from exc


def extract_image_text(
    image_source,
    language: str = "eng"
) -> dict:
    """
    Fonction principale d'extraction OCR.

    Accepte :
        - Un chemin local.
        - Des données binaires (bytes).
        - Un flux BytesIO.
        - Une image Pillow.

    Returns:
        {
            "method": "ocr",
            "text": "..."
        }
    """

    image = open_image(image_source)

    text = extract_text_from_image(
        image,
        language=language
    )

    return {
        "method": "ocr",
        "text": text
    }
