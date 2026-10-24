
from pathlib import Path
import pymupdf

BASE_DIR = Path(__file__).resolve().parent

PAPER_DIR = BASE_DIR / "data" / "papers"


def read_papers():
   
    pdf_files = list(PAPER_DIR.glob("*.pdf"))
    for pdf_file in pdf_files:
        print(pdf_file.name)


if __name__ == "__main__":
    read_papers()
