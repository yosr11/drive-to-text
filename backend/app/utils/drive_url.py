
import re
from urllib.parse import urlparse, unquote


class InvalidDriveURL(ValueError):
    """Erreur lorsque le lien Google Drive est invalide."""
    pass


def extract_folder_id(folder_url: str) -> str:
    """
    Extrait le Folder ID depuis un lien Google Drive.

    Exemple :
    https://drive.google.com/drive/folders/ABC123xyz
    retourne ABC123xyz.
    
    """

    if not folder_url or not isinstance(folder_url, str):
        raise InvalidDriveURL("Le lien Google Drive est vide.")

    folder_url = folder_url.strip()

    # Accepter les URL avec ou sans https://
    if not re.match(r"^https?://", folder_url, re.IGNORECASE):
        folder_url = "https://" + folder_url

    parsed_url = urlparse(folder_url)

    # Vérifier le domaine
    if parsed_url.hostname not in {
        "drive.google.com",
        "www.drive.google.com"
    }:
        raise InvalidDriveURL(
            "Le domaine fourni n'est pas Google Drive."
        )

    # Chercher le Folder ID dans le chemin
    match = re.search(
        r"/folders/([^/?#]+)",
        parsed_url.path
    )

    if not match:
        raise InvalidDriveURL(
            "Impossible de trouver le Folder ID dans le lien."
        )

    folder_id = unquote(match.group(1))

    # Vérifier le format de l'identifiant
    if not re.fullmatch(r"[A-Za-z0-9_-]+", folder_id):
        raise InvalidDriveURL(
            "Le Folder ID contient des caractères invalides."
        )

    return folder_id
