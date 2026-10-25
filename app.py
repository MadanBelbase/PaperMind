from pathlib import Path
import pymupdf

BASE_DIR = Path(__file__).resolve().parent
PAPER_DIR = BASE_DIR / "data" / "papers"

# Suppress raw MuPDF library errors from spamming the console
pymupdf.TOOLS.mupdf_display_errors(False)


def load_pdfs(paper_dir):
    documents = {}
    if not paper_dir.exists():
        print(f"Directory {paper_dir} does not exist.")
        return documents

    for pdf_file in paper_dir.glob("*.pdf"):
        try:
            doc = pymupdf.open(pdf_file)

            if doc.is_repaired:
                print(
                    f"Skipped {pdf_file.name}: File is corrupted or incomplete."
                )
                doc.close()
                continue

            text = ""
            for page in doc:
                page_text = page.get_text()
                if not page_text.strip():
                    try:
                        page_text = page.get_text("text", flags=pymupdf.TEXTFLAGS_SEARCH)
                    except Exception as ocr_err:
                        page_text = f"[OCR Failed on page {page.number}: {ocr_err}]"

                text += page_text + "\n"

            documents[pdf_file.name] = text
            print(f"Loaded {pdf_file.name} successfully.")
            doc.close()

        except Exception as e:
            print(f"Failed to process {pdf_file.name}: {e}")

    return documents


if __name__ == "__main__":
    documents = load_pdfs(PAPER_DIR)

    if documents:
        first_pdf = next(iter(documents))
        print(f"\nPreview of {first_pdf}:")
        print(documents[first_pdf][:1000])
