
import pymupdf

from app.services.drive_service import download_file_content


file_id = "1ZzKIAZIWNWFGv4CtuZjF_AN31XpRW-Tv"

# Télécharger le PDF depuis Google Drive
pdf_bytes = download_file_content(file_id)

# Ouvrir le PDF avec PyMuPDF
doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")

# Examiner chaque page
for page_number, page in enumerate(doc, start=1):

    print(f"\n--- Page {page_number} ---")

    images = page.get_images(full=True)

    for image in images:
        xref = image[0]

        print("Image XREF :", xref)
        print("Dimensions :", image[2], "x", image[3])
        print("Emplacements :", page.get_image_rects(xref))

doc.close()
