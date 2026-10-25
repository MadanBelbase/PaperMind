from pathlib import Path
import chromadb
import ollama
from tqdm import tqdm

BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / "chroma_db"
OLLAMA_MODEL = "llama3.2:3b"

def generate_and_store_summaries():
    if not DB_DIR.exists():
        print("❌ Error: Run your main app.py pipeline first to load raw text.")
        return

    chroma_client = chromadb.PersistentClient(path=str(DB_DIR))
    source_collection = chroma_client.get_collection(name="academic_papers")
    summary_collection = chroma_client.get_or_create_collection(name="paper_summaries")

    # Fetch all data to extract unique paper titles
    print("📋 Scanning existing vector database...")
    all_records = source_collection.get(include=["metadatas", "documents"])
    
    # Group raw text chunks by paper name
    paper_data = {}
    for text, meta in zip(all_records["documents"], all_records["metadatas"]):
        source = meta["source"]
        if source not in paper_data:
            paper_data[source] = []
        # Gather up to the first 12 chunks (approx 3-4 pages including Abstract/Intro)
        if len(paper_data[source]) < 12:
            paper_data[source].append(text)

    print(f"🚀 Found {len(paper_data)} distinct papers. Profiling high-level details...")

    for paper_name, chunks in tqdm(paper_data.items(), desc="Summarizing Papers"):
        # Check if already summarized to avoid wasting CPU cycles
        existing = summary_collection.get(ids=[f"summary_{paper_name}"])
        if existing["ids"]:
            continue

        combined_intro = "\n".join(chunks)
        
        prompt = (
            f"Analyze the following text fragments from the research paper titled '{paper_name}'.\n"
            "Extract and generate a highly concise summary covering exactly these three attributes:\n"
            "1. CORE METHODOLOGY / ALGORITHMS USED (e.g., YOLOv7, CNN, U-Net, CLAHE)\n"
            "2. DATASETS USED OR INTRODUCED\n"
            "3. PRIMARY RESEARCH GOAL\n\n"
            f"--- PAPER TEXT EXTRACTS ---\n{combined_intro[:6000]}"
        )

        try:
            response = ollama.generate(model=OLLAMA_MODEL, prompt=prompt)
            summary_text = response["response"]

            # Save the structural summary into the summaries collection
            summary_collection.add(
                ids=[f"summary_{paper_name}"],
                documents=[summary_text],
                metadatas=[{"source": paper_name, "type": "global_summary"}]
            )
        except Exception as e:
            print(f"⚠️ Failed summarizing {paper_name}: {e}")

    print("\n🏁 Summary database profiling complete! You can now use global search queries.")

if __name__ == "__main__":
    generate_and_store_summaries()
