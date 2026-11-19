
from app.services.drive_service import list_folder_files
from app.services.batch_service import (
    create_batch,
    process_batch,
    get_batch_result
)
from app.utils.drive_url import extract_folder_id


FOLDER_URL = (
    "https://drive.google.com/drive/folders/"
    "12U8yuf2EOL5UPj2RF4uIJ8VJSUnjI32J"
)


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
