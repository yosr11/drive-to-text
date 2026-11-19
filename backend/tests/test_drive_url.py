
import pytest

from app.utils.drive_url import (
    extract_folder_id,
    InvalidDriveURL
)


# Liens Google Drive valides
@pytest.mark.parametrize(
    ("url", "expected_id"),
    [
        (
            "https://drive.google.com/drive/folders/ABC123xyz",
            "ABC123xyz"
        ),
        (
            "https://www.drive.google.com/drive/folders/ABC123xyz",
            "ABC123xyz"
        ),
        (
            "drive.google.com/drive/folders/ABC123xyz",
            "ABC123xyz"
        ),
        (
            "https://drive.google.com/drive/folders/ABC123_xyz-456",
            "ABC123_xyz-456"
        ),
        (
            "https://drive.google.com/drive/folders/ABC123xyz?usp=sharing",
            "ABC123xyz"
        ),
    ]
)
def test_extract_valid_folder_id(url, expected_id):
    assert extract_folder_id(url) == expected_id


# Liens vides ou incorrects
@pytest.mark.parametrize(
    "url",
    [
        "",
        "   ",
        None,
        123,
    ]
)
def test_extract_invalid_empty_url(url):
    with pytest.raises(InvalidDriveURL):
        extract_folder_id(url)


# Domaine incorrect
@pytest.mark.parametrize(
    "url",
    [
        "https://example.com/drive/folders/ABC123",
        "https://docs.google.com/drive/folders/ABC123",
        "https://fake-drive.google.com/drive/folders/ABC123",
    ]
)
def test_reject_invalid_domain(url):
    with pytest.raises(InvalidDriveURL):
        extract_folder_id(url)


# Folder ID absent
@pytest.mark.parametrize(
    "url",
    [
        "https://drive.google.com/",
        "https://drive.google.com/drive/my-drive",
        "https://drive.google.com/file/d/ABC123",
    ]
)
def test_reject_missing_folder_id(url):
    with pytest.raises(InvalidDriveURL):
        extract_folder_id(url)


# Folder ID contenant des caractères invalides
@pytest.mark.parametrize(
    "url",
    [
        "https://drive.google.com/drive/folders/ABC@123",
        "https://drive.google.com/drive/folders/ABC.123",
        "https://drive.google.com/drive/folders/ABC%20123",
    ]
)
def test_reject_invalid_folder_id(url):
    with pytest.raises(InvalidDriveURL):
        extract_folder_id(url)


# Espaces autour du lien
def test_extract_folder_id_with_spaces():
    url = "  https://drive.google.com/drive/folders/ABC123xyz  "

    assert extract_folder_id(url) == "ABC123xyz"
