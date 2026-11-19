
import requests

from app.config import (
    GOOGLE_DRIVE_API_KEY,
    GOOGLE_DRIVE_API_BASE_URL,
)


# Types MIME acceptés
SUPPORTED_MIME_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
}

PAGE_SIZE = 1000
REQUEST_TIMEOUT = 30


# Exceptions personnalisées

class DriveServiceError(Exception):
    """Erreur générale du service Google Drive."""
    pass


class FolderNotFoundError(DriveServiceError):
    """Dossier inexistant ou inaccessible."""
    pass


class PrivateFolderError(DriveServiceError):
    """Dossier non accessible publiquement."""
    pass


class GoogleDriveAPIError(DriveServiceError):
    """Erreur retournée par Google Drive API."""
    pass


class DriveFileNotFoundError(DriveServiceError):
    """Fichier Google Drive introuvable ou inaccessible."""
    pass


def _handle_api_error(response):
    """
    Analyse les erreurs retournées par Google Drive.
    """

    try:
        error_data = response.json().get("error", {})
        message = error_data.get("message", "Erreur inconnue")
    except ValueError:
        message = response.text or "Erreur inconnue"

    if response.status_code == 404:
        raise FolderNotFoundError(
            "Dossier inexistant ou introuvable."
        )

    if response.status_code == 403:
        raise PrivateFolderError(
            "Accès refusé : vérifiez que le dossier est public "
            "et que votre clé API est valide. Détail : " + message
        )

    raise GoogleDriveAPIError(
        f"Google Drive API ({response.status_code}) : {message}"
    )


def get_folder_metadata(folder_id: str) -> dict:
    """
    Vérifie l'existence et l'accessibilité du dossier.
    Retourne ses métadonnées.
    """

    url = f"{GOOGLE_DRIVE_API_BASE_URL}/files/{folder_id}"

    params = {
        "key": GOOGLE_DRIVE_API_KEY,
        "fields": "id,name,mimeType",
        "supportsAllDrives": "true",
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=REQUEST_TIMEOUT,
        )

    except requests.Timeout as exc:
        raise DriveServiceError(
            "Délai dépassé lors de la connexion à Google Drive."
        ) from exc

    except requests.RequestException as exc:
        raise DriveServiceError(
            f"Erreur de connexion à Google Drive : {exc}"
        ) from exc

    if not response.ok:
        _handle_api_error(response)

    folder = response.json()

    if folder.get("mimeType") != "application/vnd.google-apps.folder":
        raise DriveServiceError(
            "L'identifiant fourni ne correspond pas à un dossier."
        )

    return folder


def list_folder_files(folder_id: str) -> dict:
    """
    Récupère tous les fichiers PDF, PNG et JPEG
    d'un dossier Google Drive public.

    Gère automatiquement la pagination.
    """

    # Vérifier d'abord le dossier
    folder = get_folder_metadata(folder_id)

    url = f"{GOOGLE_DRIVE_API_BASE_URL}/files"

    # Construire le filtre Google Drive
    mime_filter = " or ".join(
        f"mimeType = '{mime_type}'"
        for mime_type in SUPPORTED_MIME_TYPES
    )

    query = (
        f"'{folder_id}' in parents "
        f"and trashed = false "
        f"and ({mime_filter})"
    )

    params = {
        "key": GOOGLE_DRIVE_API_KEY,
        "q": query,
        "pageSize": PAGE_SIZE,
        "fields": (
            "nextPageToken,"
            "files(id,name,mimeType,size)"
        ),
        "orderBy": "name",
        "supportsAllDrives": "true",
        "includeItemsFromAllDrives": "true",
    }

    all_files = []

    try:
        while True:

            response = requests.get(
                url,
                params=params,
                timeout=REQUEST_TIMEOUT,
            )

            if not response.ok:
                _handle_api_error(response)

            data = response.json()

            files = data.get("files", [])

            # Ajouter les fichiers de la page actuelle
            for file in files:

                all_files.append({
                    "id": file.get("id"),
                    "name": file.get("name"),
                    "mimeType": file.get("mimeType"),
                    "size": file.get("size"),
                })

            # Vérifier s'il existe une page suivante
            next_page_token = data.get("nextPageToken")

            if not next_page_token:
                break

            # Demander la page suivante
            params["pageToken"] = next_page_token

    except requests.Timeout as exc:
        raise DriveServiceError(
            "Délai dépassé pendant la récupération des fichiers."
        ) from exc

    except requests.RequestException as exc:
        raise DriveServiceError(
            f"Erreur réseau : {exc}"
        ) from exc

    return {
        "folder_id": folder["id"],
        "folder_name": folder["name"],
        "total_files": len(all_files),
        "files": all_files,
    }


def download_file_content(file_id: str) -> bytes:
    """
    Récupère le contenu d'un fichier depuis Google Drive
    directement en mémoire, sans sauvegarde locale.

    Args:
        file_id: Identifiant du fichier Google Drive.

    Returns:
        Le contenu binaire du fichier.
    """

    url = f"{GOOGLE_DRIVE_API_BASE_URL}/files/{file_id}"

    params = {
        "key": GOOGLE_DRIVE_API_KEY,
        "alt": "media",
        "supportsAllDrives": "true",
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=REQUEST_TIMEOUT,
        )

        if not response.ok:
            if response.status_code == 404:
                raise DriveFileNotFoundError(
                    "Fichier Google Drive introuvable ou inaccessible."
                )

            _handle_api_error(response)

        content = response.content

        if not content:
            raise DriveServiceError(
                "Le fichier récupéré depuis Google Drive est vide."
            )

        return content

    except requests.Timeout as exc:
        raise DriveServiceError(
            "Délai dépassé pendant le téléchargement du fichier."
        ) from exc

    except requests.RequestException as exc:
        raise DriveServiceError(
            f"Erreur réseau pendant le téléchargement : {exc}"
        ) from exc
