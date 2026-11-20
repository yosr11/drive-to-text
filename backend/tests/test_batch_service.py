
from app.services.drive_service import list_folder_files
from app.services.batch_service import (
    create_batch,
    process_batch,
    get_batch_result
)
from app.services import batch_service
from app.utils.drive_url import extract_folder_id


FOLDER_URL = (
    "https://drive.google.com/drive/folders/"
    "12U8yuf2EOL5UPj2RF4uIJ8VJSUnjI32J"
)


def test_batch_result_exposes_per_file_progress(monkeypatch):
    batch = create_batch([
        {"id": "file-1", "name": "one.pdf", "mimeType": "application/pdf"},
        {"id": "file-2", "name": "two.png", "mimeType": "image/png"},
    ])
    observed_progress = []

    def finish_file(file_result, language):
        if file_result["file_id"] == "file-1":
            file_result["status"] = "done"
        else:
            observed_progress.append(get_batch_result(batch["batch_id"]))
            file_result["status"] = "failed"

    monkeypatch.setattr(batch_service, "process_single_file", finish_file)

    result = process_batch(batch["batch_id"])

    assert observed_progress[0]["status"] == "processing"
    assert observed_progress[0]["results"][0]["status"] == "done"
    assert observed_progress[0]["successful_files"] == 1
    assert result["status"] == "done"
    assert result["successful_files"] == 1
    assert result["failed_files"] == 1


def test_batch_processing():

    # 1. Récupérer les fichiers Google Drive
    folder_id = extract_folder_id(FOLDER_URL)
    folder_data = list_folder_files(folder_id)

    files = folder_data["files"]

    # 2. Créer le batch
    batch = create_batch(files)

    print("\nBatch créé :")
    print("ID :", batch["batch_id"])
    print("Nombre de fichiers :", batch["total_files"])

    # 3. Vérifier le statut initial
    for file in batch["results"]:
        assert file["status"] == "pending"

    # 4. Traiter le batch
    result = process_batch(
        batch["batch_id"],
        language="eng+fra"
    )

    # 5. Afficher les statistiques
    print("\nRésultat du batch :")
    print("Statut :", result["status"])
    print("Total :", result["total_files"])
    print("Réussites :", result["successful_files"])
    print("Échecs :", result["failed_files"])

    # 6. Afficher le résultat de chaque fichier
    for file in result["results"]:
        print("\nFichier :", file["filename"])
        print("Statut :", file["status"])
        print("Méthode :", file["method"])

        if file["status"] == "failed":
            print("Erreur :", file["error"])
        else:
            print("Texte extrait :", file["text"][:200])

    # 7. Vérifier la construction du JSON
    json_result = get_batch_result(batch["batch_id"])

    assert json_result["total_files"] == (
        json_result["successful_files"]
        + json_result["failed_files"]
    )

    print("\nTest terminé avec succès.")


if __name__ == "__main__":
    test_batch_processing()
