from pathlib import Path
import chromadb
import ollama

BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / "chroma_db"
OLLAMA_MODEL = "llama3.2:3b"


def retrieve_global_knowledge() -> str:
    """
    Pulls the high-level summary blueprints of ALL papers simultaneously.
    """
    chroma_client = chromadb.PersistentClient(path=str(DB_DIR))
    try:
        collection = chroma_client.get_collection(name="paper_summaries")
        results = collection.get(include=["documents", "metadatas"])
        
        compiled_summaries = []
        for doc, meta in zip(results["documents"], results["metadatas"]):
            compiled_summaries.append(f" Paper: {meta['source']}\n{doc}\n")
        
        return "\n".join(compiled_summaries)
    except Exception:
        return ""


def retrieve_deep_chunks(query_text: str, n_results: int = 4) -> str:
    chroma_client = chromadb.PersistentClient(path=str(DB_DIR))
    try:
        collection = chroma_client.get_collection(name="academic_papers")
        results = collection.query(query_texts=[query_text], n_results=n_results)
        
        context_blocks = []
        for doc_text, meta in zip(results["documents"][0], results["metadatas"][0]):
            context_blocks.append(f"[Source Paper: {meta['source']} | Page: {meta['page']}]\nText: {doc_text.strip()}")
        return "\n\n---\n\n".join(context_blocks)
    except Exception:
        return ""


def ask_rag_engine(user_question: str, mode: str = "deep"):
    if mode == "global":
        print("🌐 Scanning global cross-paper summaries portfolio...")
        context = retrieve_global_knowledge()
        system_instruction = (
            "You are PaperMind, an elite academic advisor analyzing a full collection of papers.\n"
            "Using the comprehensive summaries provided below, provide a global cross-paper synthesis answer.\n"
            "Compare, count, or identify trends across the papers explicitly using their titles.\n"
        )
    else:
        print("🔍 Searching deep paragraph-level text chunks...")
        context = retrieve_deep_chunks(user_question, n_results=4)
        system_instruction = (
            "You are PaperMind. Answer the question using ONLY the narrow text snippets provided.\n"
            "Always cite the exact Source Paper name and Page number.\n"
        )

    if not context:
        print("⚠️ No database context available. Please verify your collection loads.")
        return

    full_system_prompt = f"{system_instruction}\n\n{context}\"

    print(f"🧠 Computing with Ollama ({OLLAMA_MODEL})...\n")
    try:
        response_stream = ollama.generate(
            model=OLLAMA_MODEL,
            prompt=f"Question: {user_question}",
            system=full_system_prompt,
            stream=True,
        )

        print("🤖 PaperMind Answer:")
        for chunk in response_stream:
            print(chunk["response"], end="", flush=True)
    except Exception as e:
        print(f" Execution error: {e}")


if __name__ == "__main__":
    print("PaperMind Hybrid RAG Engine Online.")
    print("Standard mode: Searches inside individual page snippets.")
    print("Global mode: Type 'global ' before your question to look across ALL papers details.")

    while True:
        query = input("\nAsk PaperMind (or 'exit'): ").strip()
        if query.lower() in ["exit", "quit"]:
            break
        if not query:
            continue

        if query.lower().startswith("global "):
            actual_question = query[7:].strip()
            ask_rag_engine(actual_question, mode="global")
        else:
            ask_rag_engine(query, mode="deep")
