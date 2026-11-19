
import pytest
from io import BytesIO
from pathlib import Path
from PIL import Image

from app.services.ocr_service import (
    open_image,
    validate_language,
    extract_text_from_image,
    extract_image_text,
    OCRExtractionError,
    InvalidImageError,
    EmptyImageError,
    OCRLanguageError,
    TesseractNotAvailableError,
    SUPPORTED_LANGUAGES,
)

import pytesseract


# --------------------------------------------------
# Fixtures
# --------------------------------------------------

@pytest.fixture
def sample_image():
    """Crée une image RGB de test."""
    return Image.new("RGB", (100, 100), color="white")


@pytest.fixture
def sample_image_bytes(sample_image):
    """Convertit l'image de test en bytes."""
    buffer = BytesIO()
    sample_image.save(buffer, format="PNG")
    return buffer.getvalue()


@pytest.fixture
def sample_image_file(sample_image, tmp_path):
    """Crée un fichier image temporaire."""
    path = tmp_path / "test.png"
    sample_image.save(path)
    return path


# --------------------------------------------------
# Tests de open_image()
# --------------------------------------------------

def test_open_image_from_pillow(sample_image):
    image = open_image(sample_image)

    assert isinstance(image, Image.Image)
    assert image.mode == "RGB"
    assert image.size == (100, 100)


def test_open_image_from_bytes(sample_image_bytes):
    image = open_image(sample_image_bytes)

    assert isinstance(image, Image.Image)
    assert image.mode == "RGB"


def test_open_image_from_bytesio(sample_image_bytes):
    image_stream = BytesIO(sample_image_bytes)

    image = open_image(image_stream)

    assert isinstance(image, Image.Image)
    assert image.mode == "RGB"


def test_open_image_from_path(sample_image_file):
    image = open_image(sample_image_file)

    assert isinstance(image, Image.Image)
    assert image.mode == "RGB"


def test_open_image_empty_bytes():
    with pytest.raises(EmptyImageError):
        open_image(b"")


def test_open_image_empty_bytesio():
    with pytest.raises(EmptyImageError):
        open_image(BytesIO(b""))


def test_open_image_empty_file(tmp_path):
    empty_file = tmp_path / "empty.png"
    empty_file.write_bytes(b"")

    with pytest.raises(EmptyImageError):
        open_image(empty_file)


def test_open_image_file_not_found():
    with pytest.raises(FileNotFoundError):
        open_image("image_inexistante.png")


def test_open_image_invalid_bytes():
    with pytest.raises(InvalidImageError):
        open_image(b"ceci n'est pas une image")


def test_open_image_invalid_source():
    with pytest.raises(TypeError):
        open_image(123)


def test_open_image_converts_rgba_to_rgb():
    image = Image.new("RGBA", (100, 100), color="white")

    result = open_image(image)

    assert result.mode == "RGB"


# --------------------------------------------------
# Tests de validate_language()
# --------------------------------------------------

@pytest.mark.parametrize(
    "language",
    list(SUPPORTED_LANGUAGES)
)
def test_validate_language_supported(language):
    validate_language(language)


@pytest.mark.parametrize(
    "language",
    ["deu", "ita", "spa", "", "ENG", None, 123]
)
def test_validate_language_unsupported(language):
    with pytest.raises(OCRLanguageError):
        validate_language(language)


# --------------------------------------------------
# Tests de extract_text_from_image()
# --------------------------------------------------

def test_extract_text_from_image_success(sample_image, monkeypatch):
    def mock_image_to_string(image, lang):
        return "  Texte détecté  "

    monkeypatch.setattr(
        pytesseract,
        "image_to_string",
        mock_image_to_string
    )

    result = extract_text_from_image(sample_image, language="eng")

    assert result == "Texte détecté"


def test_extract_text_from_image_invalid_language(sample_image):
    with pytest.raises(OCRLanguageError):
        extract_text_from_image(sample_image, language="deu")


def test_extract_text_from_image_tesseract_not_found(
    sample_image,
    monkeypatch
):
    def mock_image_to_string(image, lang):
        raise pytesseract.pytesseract.TesseractNotFoundError()

    monkeypatch.setattr(
        pytesseract,
        "image_to_string",
        mock_image_to_string
    )

    with pytest.raises(TesseractNotAvailableError):
        extract_text_from_image(sample_image)


def test_extract_text_from_image_tesseract_error(
    sample_image,
    monkeypatch
):
    def mock_image_to_string(image, lang):
        raise pytesseract.pytesseract.TesseractError(1, "Erreur OCR")

    monkeypatch.setattr(
        pytesseract,
        "image_to_string",
        mock_image_to_string
    )

    with pytest.raises(OCRLanguageError):
        extract_text_from_image(sample_image)


def test_extract_text_from_image_unexpected_error(
    sample_image,
    monkeypatch
):
    def mock_image_to_string(image, lang):
        raise RuntimeError("Erreur inattendue")

    monkeypatch.setattr(
        pytesseract,
        "image_to_string",
        mock_image_to_string
    )

    with pytest.raises(OCRExtractionError):
        extract_text_from_image(sample_image)


# --------------------------------------------------
# Tests de extract_image_text()
# --------------------------------------------------

def test_extract_image_text_success(sample_image, monkeypatch):
    def mock_extract(image, language="eng"):
        return "Texte OCR détecté"

    monkeypatch.setattr(
        "app.services.ocr_service.extract_text_from_image",
        mock_extract
    )

    result = extract_image_text(sample_image, language="eng")

    assert result["method"] == "ocr"
    assert result["text"] == "Texte OCR détecté"


def test_extract_image_text_from_bytes(
    sample_image_bytes,
    monkeypatch
):
    def mock_extract(image, language="eng"):
        return "Texte extrait depuis bytes"

    monkeypatch.setattr(
        "app.services.ocr_service.extract_text_from_image",
        mock_extract
    )

    result = extract_image_text(sample_image_bytes)

    assert result["method"] == "ocr"
    assert result["text"] == "Texte extrait depuis bytes"


def test_extract_image_text_invalid_image():
    with pytest.raises(InvalidImageError):
        extract_image_text(b"faux contenu image")


def test_extract_image_text_invalid_language(
    sample_image,
    monkeypatch
):
    def mock_extract(image, language="eng"):
        raise OCRLanguageError("Langue invalide")

    monkeypatch.setattr(
        "app.services.ocr_service.extract_text_from_image",
        mock_extract
    )

    with pytest.raises(OCRLanguageError):
        extract_image_text(sample_image, language="deu")
