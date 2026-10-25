from pathlib import Path
import chromadb

BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / "chroma_db"

def get_all_papers():
    """
    Fetches all distinct paper filenames currently indexed inside ChromaDB.
    """
    if not DB_DIR.exists():
        print(f"❌ Error: Database path '{DB_DIR}' not found.")
        return

    chroma_client = chromadb.PersistentClient(path=str(DB_DIR))
    try:
        collection = chroma_client.get_collection(name="academic_papers")
        
        # Get all metadatas from the DB
        results = collection.get(include=["metadatas"])
        
        # Extract unique source names using a set
        unique_papers = sorted(list(set(item["source"] for item in results["metadatas"] if "source" in item)))
        
        print(f"\n📚 Current Indexed Papers ({len(unique_papers)} total):")
        print(f"=======================================================")
        for idx, paper in enumerate(unique_papers, 1):
            print(f"  {idx}. {paper}")
        print(f"=======================================================")
    except Exception as e:
        print(f"❌ Error listing papers: {e}")


def search_knowledge_base(query_text: str, n_results: int = 4):
    if not DB_DIR.exists():
        print(f"❌ Error: Vector database directory '{DB_DIR}' not found.")
        return

    chroma_client = chromadb.PersistentClient(path=str(DB_DIR))
    try:
        collection = chroma_client.get_collection(name="academic_papers")
    except Exception:
        print("❌ Error: Collection 'academic_papers' not found.")
        return

    results = collection.query(query_texts=[query_text], n_results=n_results)

    print(f"\n🔍 Search Query: '{query_text}'")
    print(f"=======================================================")
    
    documents = results['documents'][0]
    metadatas = results['metadatas'][0]
    distances = results['distances'][0]

    for idx, (doc_text, meta, score) in enumerate(zip(documents, metadatas, distances)):
        print(f"\n📌 [Result #{idx + 1}] | Source: {meta['source']} | Page: {meta['page']} | Distance Match: {score:.4f}")
        print(f"--------------------------------------------------------------------------------")
        print(f"{doc_text.strip()}")
        print(f"--------------------------------------------------------------------------------")


if __name__ == "__main__":
    print("🤖 PaperMind Vector Search Engine Active.")
    print("💡 Tip: Type 'list' to see all indexed research papers.")
    
    while True:
        user_query = input("\nEnter your search question (or type 'exit' to quit): ").strip()
        if user_query.lower() in ['exit', 'quit']:
            print("Goodbye!")
            break
        if not user_query:
            continue
            
        # Command interceptor for listing papers
        if user_query.lower() == 'list':
            get_all_papers()
        else:
            search_knowledge_base(user_query, n_results=3)
