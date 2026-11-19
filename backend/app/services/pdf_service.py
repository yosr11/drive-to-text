
from pathlib import Path
from io import BytesIO

from pypdf import PdfReader
from pypdf.errors import PdfReadError
import pymupdf

from app.services.ocr_service import extract_image_text


# Exceptions personnalisées

class PDFExtractionError(Exception):
    """Erreur générale lors de l'extraction d'un PDF."""
    pass


class EmptyPDFError(PDFExtractionError):
    """Le fichier PDF est vide ou ne contient aucune page."""
    pass


class CorruptedPDFError(PDFExtractionError):
    """Le fichier PDF est invalide ou corrompu."""
    pass


class EncryptedPDFError(PDFExtractionError):
    """Le PDF est protégé par un mot de passe."""
    pass


def open_pdf(pdf_source) -> PdfReader:
    """
    Ouvre un PDF depuis un chemin local ou depuis des données binaires.

    Args:
        pdf_source:
            - str ou Path : chemin du fichier PDF local.
            - bytes : contenu binaire du PDF.
            - BytesIO : flux PDF en mémoire.

    Returns:
        Un objet PdfReader.

    Raises:
        FileNotFoundError: fichier local introuvable.
        EmptyPDFError: fichier vide.
        CorruptedPDFError: fichier invalide ou corrompu.
        EncryptedPDFError: fichier protégé par mot de passe.
    """

    # Cas 1 : PDF reçu sous forme de bytes
    if isinstance(pdf_source, bytes):

        if not pdf_source:
            raise EmptyPDFError(
                "Le contenu du PDF est vide."
            )

        pdf_stream = BytesIO(pdf_source)

    # Cas 2 : PDF reçu sous forme de BytesIO
    elif isinstance(pdf_source, BytesIO):

        if pdf_source.getbuffer().nbytes == 0:
            raise EmptyPDFError(
                "Le contenu du PDF est vide."
            )

        pdf_stream = pdf_source
        pdf_stream.seek(0)

    # Cas 3 : PDF reçu depuis un chemin local
    elif isinstance(pdf_source, (str, Path)):

        path = Path(pdf_source)

        if not path.exists() or not path.is_file():
            raise FileNotFoundError(
                f"Fichier PDF introuvable : {pdf_source}"
            )

        if path.stat().st_size == 0:
            raise EmptyPDFError(
                "Le fichier PDF est vide."
            )

        pdf_stream = path

    else:
        raise TypeError(
            "Source PDF invalide. Fournissez un chemin local, "
            "des bytes ou un objet BytesIO."
        )

    # Vérifier la signature PDF
    if isinstance(pdf_source, bytes):
        pdf_header = pdf_source[:5]

    elif isinstance(pdf_source, BytesIO):
        current_position = pdf_stream.tell()
        pdf_stream.seek(0)
        pdf_header = pdf_stream.read(5)
        pdf_stream.seek(current_position)

    else:
        with open(pdf_stream, "rb") as pdf_file:
            pdf_header = pdf_file.read(5)

    if pdf_header != b"%PDF-":
        raise CorruptedPDFError(
            "Le fichier fourni n'est pas un PDF valide "
            "ou sa signature est incorrecte."
        )

    # Ouvrir le PDF avec pypdf
    try:
        reader = PdfReader(
            pdf_stream,
            strict=False
        )

    except (PdfReadError, OSError, ValueError) as exc:
        raise CorruptedPDFError(
            f"Impossible de lire le fichier PDF : {exc}"
        ) from exc

    except Exception as exc:
        raise CorruptedPDFError(
            f"Erreur inattendue lors de l'ouverture du PDF : {exc}"
        ) from exc

    # Vérifier si le PDF est protégé
    if reader.is_encrypted:
        raise EncryptedPDFError(
            "Le PDF est protégé par un mot de passe."
        )

    # Vérifier que le PDF contient des pages
    try:
        if len(reader.pages) == 0:
            raise EmptyPDFError(
                "Le document PDF ne contient aucune page."
            )

    except PDFExtractionError:
        raise

    except Exception as exc:
        raise CorruptedPDFError(
            f"Impossible de lire les pages du PDF : {exc}"
        ) from exc

    return reader


def extract_text_by_page(reader: PdfReader) -> str:
    """
    Extrait le texte de chaque page du PDF.

    Args:
        reader: Objet PdfReader.

    Returns:
        Le texte complet du document.
    """

    extracted_pages = []

    for page_number, page in enumerate(reader.pages, start=1):

        try:
            page_text = page.extract_text() or ""

        except Exception as exc:
            raise CorruptedPDFError(
                f"Erreur lors de l'extraction de la page "
                f"{page_number} : {exc}"
            ) from exc

        extracted_pages.append(
            f"--- Page {page_number} ---\n{page_text}"
        )

    return "\n\n".join(extracted_pages)

def extract_pdf_text_with_ocr(pdf_source, language="eng") -> dict:
    """
    Extrait le texte des PDF natifs, scannés et mixtes.

    - PDF natif : extraction avec pypdf.
    - PDF mixte : extraction native + OCR des images intégrées.
    - PDF scanné : conversion de chaque page en image avec PyMuPDF,
      puis OCR avec Tesseract.
    """

    reader = open_pdf(pdf_source)

    # Ouvrir également le PDF avec PyMuPDF
    if isinstance(pdf_source, bytes):
        doc = pymupdf.open(
            stream=pdf_source,
            filetype="pdf"
        )

    elif isinstance(pdf_source, BytesIO):
        doc = pymupdf.open(
            stream=pdf_source.getvalue(),
            filetype="pdf"
        )

    else:
        doc = pymupdf.open(str(pdf_source))

    results = []

    try:
        for page_number, pdf_page in enumerate(reader.pages):

            page_text = pdf_page.extract_text() or ""
            pymupdf_page = doc[page_number]

            # Vérifier si le texte natif est exploitable
            if len(page_text.strip()) >= 20:

                extracted_text = page_text

                # Récupérer les images intégrées
                images = pymupdf_page.get_images(full=True)

                processed_images = set()

                for image in images:
                    xref = image[0]

                    image_rects = pymupdf_page.get_image_rects(xref)

                    for rect in image_rects:
                        rect_key = (
                            round(rect.x0, 2),
                            round(rect.y0, 2),
                            round(rect.x1, 2),
                            round(rect.y1, 2)
                        )

                        if rect_key in processed_images:
                            continue

                        processed_images.add(rect_key)

                        pix = pymupdf_page.get_pixmap(
                            dpi=300,
                            clip=rect,
                            alpha=False
                        )

                        image_bytes = pix.tobytes("png")

                        ocr_result = extract_image_text(
                            image_bytes,
                            language=language
                        )

                        if ocr_result["text"].strip():
                            extracted_text += (
                                "\n\n--- Texte détecté dans une image ---\n"
                                + ocr_result["text"]
                            )

                        

            else:
                # Page scannée : convertir toute la page en image
                pix = pymupdf_page.get_pixmap(
                    dpi=300,
                    alpha=False
                )

                image_bytes = pix.tobytes("png")

                # Appliquer l'OCR sur la page entière
                ocr_result = extract_image_text(
                    image_bytes,
                    language=language
                )

                extracted_text = ocr_result["text"]

            results.append(
                f"--- Page {page_number + 1} ---\n{extracted_text}"
            )

    finally:
        doc.close()

    return {
        "method": "pdf_text_ocr",
        "text": "\n\n".join(results)
    }


def extract_pdf_text(pdf_source) -> dict:
    """
    Fonction principale d'extraction PDF.

    Accepte :
        - Un chemin local.
        - Des données binaires (bytes).
        - Un flux BytesIO.

    Ouvre le PDF, extrait son texte page par page
    et retourne le résultat.

    Returns:
        {
            "method": "pdf_text",
            "text": "..."
        }
    """

    reader = open_pdf(pdf_source)

    text = extract_text_by_page(reader)

    return {
        "method": "pdf_text",
        "text": text
    }
