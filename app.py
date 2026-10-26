from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import os
import pymupdf
import chromadb
from chunker import AcademicTextChunker

BASE_DIR = Path(__file__).resolve().parent
PAPER_DIR = BASE_DIR / "data" / "papers"
DB_DIR = BASE_DIR / "chroma_db" 


def process_single_pdf(pdf_path: Path, chunk_size: int, chunk_overlap: int) -> list[dict]:
    """
    Worker function executed in parallel across CPU cores.
    Parses pages, triggers OCR fallback, and tracks clean metadata matrices.
    """
    pymupdf.TOOLS.mupdf_display_errors(False)
    
    try:
        doc = pymupdf.open(pdf_path)
        page_chunks_accumulator = []
        chunker = AcademicTextChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        
        for page in doc:
            try:
                page_text = page.get_text()
                if not page_text.strip():
                    page_text = page.get_text("text", flags=pymupdf.TEXTFLAGS_SEARCH)
            except Exception as page_err:
                print(f"   ⚠️ Error reading Page {page.number + 1} in {pdf_path.name}: {page_err}")
                page_text = ""
            
            if page_text.strip():
                # Split on a per-page level to capture context accurately
                raw_page_chunks = chunker.split_text(page_text)
                for index, chunk in enumerate(raw_page_chunks):
                    page_chunks_accumulator.append({
                        "text": chunk,
                        "metadata": {
                            "source": pdf_path.name,
                            "page": page.number + 1,
                            "chunk_segment_id": index
                        }
                    })
        
        doc.close()
        
        if not page_chunks_accumulator:
            print(f"   Diagnostic Alert: '{pdf_path.name}' yielded zero text. Ensure Tesseract OCR is system configured.")
            
        return page_chunks_accumulator

    except Exception as file_err:
        print(f" Critical engine error processing {pdf_path.name}: {file_err}")
        return []


def stream_pipeline_batches(paper_dir: Path, chunk_size: int = 1000, chunk_overlap: int = 200, batch_size: int = 5):
    """
    Dispatches file parsing across multiple processes and yields documents in micro-batches.
    """
    if not paper_dir.exists():
        print(f"Directory {paper_dir} does not exist.")
        return

    pdf_files = list(paper_dir.glob("*.pdf"))
    total_files = len(pdf_files)
    print(f"🚀 Found {total_files} papers. Dispatching to CPU pool workers...\n")

    max_workers = max(1, os.cpu_count() - 1)
    batch = []
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        future_to_pdf = {
            executor.submit(process_single_pdf, pdf, chunk_size, chunk_overlap): pdf 
            for pdf in pdf_files
        }
        
        for future in as_completed(future_to_pdf):
            pdf_path = future_to_pdf[future]
            try:
                pdf_docs = future.result()
                if pdf_docs:
                    batch.extend(pdf_docs)
                    print(f"Finished: {pdf_path.name} (Generated {len(pdf_docs)} chunks)")
                else:
                    print(f" Skipped or Empty: {pdf_path.name}")
            except Exception as exc:
                print(f" Worker crashed for {pdf_path.name}: {exc}")
            
            while len(batch) >= batch_size:
                yield batch[:batch_size]
                batch = batch[batch_size:]
                
    if batch:
        yield batch


if __name__ == "__main__":
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    BATCH_SIZE = 50  
    
    chroma_client = chromadb.PersistentClient(path=str(DB_DIR))
    collection = chroma_client.get_or_create_collection(name="academic_papers")
    
    total_payload_count = 0
    unique_id_counter = 0
    
    for batch_idx, document_batch in enumerate(stream_pipeline_batches(PAPER_DIR, CHUNK_SIZE, CHUNK_OVERLAP, BATCH_SIZE)):
        total_payload_count += len(document_batch)
        
        batch_ids = []
        batch_documents = []
        batch_metadatas = []
        
        for doc in document_batch:
            clean_filename = doc['metadata']['source'].replace(" ", "_")
            doc_id = f"{clean_filename}_p{doc['metadata']['page']}_c{doc['metadata']['chunk_segment_id']}_{unique_id_counter}"
            
            batch_ids.append(doc_id)
            batch_documents.append(doc['text'])
            batch_metadatas.append(doc['metadata'])
            unique_id_counter += 1
            
        collection.add(
            ids=batch_ids,
            documents=batch_documents,
            metadatas=batch_metadatas
        )
        print(f"📦 [BATCH {batch_idx}] Successfully wrote {len(document_batch)} vector payloads to ChromaDB storage.\n")
        
    print(f"\n🏁 Ingestion complete! Processed and indexed a total of {total_payload_count} chunks.")
