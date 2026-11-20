
from io import BytesIO
from pathlib import Path

import pytest
import pymupdf

from app.services import pdf_service


@pytest.fixture
def sample_pdf(tmp_path):
    """Crée un PDF contenant du texte."""
    path = tmp_path / "sample.pdf"

    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Ceci est un document PDF de test.")
    doc.save(path)
    doc.close()

    return path


@pytest.fixture
def scanned_pdf(tmp_path):
    """Crée un PDF avec une page sans texte natif."""
    path = tmp_path / "scanned.pdf"

    doc = pymupdf.open()
    doc.new_page()
    doc.save(path)
    doc.close()

    return path


# --------------------------------------------------
# Tests de open_pdf()
# --------------------------------------------------

def test_open_pdf_from_path(sample_pdf):
    reader = pdf_service.open_pdf(sample_pdf)

    assert len(reader.pages) == 1


def test_open_pdf_from_bytes(sample_pdf):
    content = sample_pdf.read_bytes()

    reader = pdf_service.open_pdf(content)

    assert len(reader.pages) == 1


def test_open_pdf_from_bytesio(sample_pdf):
    content = sample_pdf.read_bytes()

    reader = pdf_service.open_pdf(BytesIO(content))

    assert len(reader.pages) == 1


def test_open_pdf_file_not_found(tmp_path):
    path = tmp_path / "missing.pdf"

    with pytest.raises(FileNotFoundError):
        pdf_service.open_pdf(path)


def test_open_pdf_empty_file(tmp_path):
    path = tmp_path / "empty.pdf"
    path.write_bytes(b"")

    with pytest.raises(pdf_service.EmptyPDFError):
        pdf_service.open_pdf(path)


def test_open_pdf_empty_bytes():
    with pytest.raises(pdf_service.EmptyPDFError):
        pdf_service.open_pdf(b"")


def test_open_pdf_empty_bytesio():
    with pytest.raises(pdf_service.EmptyPDFError):
        pdf_service.open_pdf(BytesIO())


def test_open_pdf_invalid_signature():
    with pytest.raises(pdf_service.CorruptedPDFError):
        pdf_service.open_pdf(b"NOT A PDF FILE")


def test_open_pdf_corrupted_content():
    with pytest.raises(pdf_service.CorruptedPDFError):
        pdf_service.open_pdf(b"%PDF-invalid-content")


def test_open_pdf_invalid_source_type():
    with pytest.raises(TypeError):
        pdf_service.open_pdf(123)


def test_open_pdf_encrypted(tmp_path):
    path = tmp_path / "encrypted.pdf"

    doc = pymupdf.open()
    doc.new_page()
    doc.save(
        path,
        encryption=pymupdf.PDF_ENCRYPT_AES_256,
        owner_pw="owner",
        user_pw="user"
    )
    doc.close()

    with pytest.raises(pdf_service.EncryptedPDFError):
        pdf_service.open_pdf(path)


# --------------------------------------------------
# Tests de extract_text_by_page()
# --------------------------------------------------

def test_extract_text_by_page(sample_pdf):
    reader = pdf_service.open_pdf(sample_pdf)

    text = pdf_service.extract_text_by_page(reader)

    assert "--- Page 1 ---" in text
    assert "Ceci est un document PDF de test." in text


def test_extract_text_by_page_multiple_pages(tmp_path):
    path = tmp_path / "multiple.pdf"

    doc = pymupdf.open()

    page1 = doc.new_page()
    page1.insert_text((72, 72), "Texte de la premiere page.")

    page2 = doc.new_page()
    page2.insert_text((72, 72), "Texte de la deuxieme page.")

    doc.save(path)
    doc.close()

    reader = pdf_service.open_pdf(path)
    text = pdf_service.extract_text_by_page(reader)

    assert "--- Page 1 ---" in text
    assert "--- Page 2 ---" in text
    assert "premiere page" in text
    assert "deuxieme page" in text


# --------------------------------------------------
# Tests de extract_pdf_text()
# --------------------------------------------------

def test_extract_pdf_text(sample_pdf):
    result = pdf_service.extract_pdf_text(sample_pdf)

    assert result["method"] == "pdf_text"
    assert "Ceci est un document PDF de test." in result["text"]


def test_extract_pdf_text_from_bytes(sample_pdf):
    content = sample_pdf.read_bytes()

    result = pdf_service.extract_pdf_text(content)

    assert result["method"] == "pdf_text"
    assert "Ceci est un document PDF de test." in result["text"]


# --------------------------------------------------
# Tests de extract_pdf_text_with_ocr()
# --------------------------------------------------

def test_extract_pdf_text_with_ocr_scanned(
    scanned_pdf,
    monkeypatch
):
    def fake_ocr(image_bytes, language="eng"):
        return {"text": "Texte détecté par OCR"}

    monkeypatch.setattr(
        pdf_service,
        "extract_image_text",
        fake_ocr
    )

    result = pdf_service.extract_pdf_text_with_ocr(
        scanned_pdf,
        language="fra"
    )

    assert result["method"] == "pdf_text_ocr"
    assert "Texte détecté par OCR" in result["text"]


def test_extract_pdf_text_with_ocr_native(
    sample_pdf,
    monkeypatch
):
    def fake_ocr(image_bytes, language="eng"):
        return {"text": ""}

    monkeypatch.setattr(
        pdf_service,
        "extract_image_text",
        fake_ocr
    )

    result = pdf_service.extract_pdf_text_with_ocr(sample_pdf)

    assert result["method"] == "pdf_text"
    assert "Ceci est un document PDF de test." in result["text"]


def test_extract_pdf_text_with_ocr_bytes(
    scanned_pdf,
    monkeypatch
):
    def fake_ocr(image_bytes, language="eng"):
        return {"text": "OCR depuis bytes"}

    monkeypatch.setattr(
        pdf_service,
        "extract_image_text",
        fake_ocr
    )

    content = scanned_pdf.read_bytes()

    result = pdf_service.extract_pdf_text_with_ocr(
        content,
        language="eng"
    )

    assert result["method"] == "pdf_text_ocr"
    assert "OCR depuis bytes" in result["text"]
