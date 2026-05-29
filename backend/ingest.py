import os
import fitz  # PyMuPDF
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

load_dotenv()

DOCS_FOLDER = "./documents"
CHROMA_PATH = "./chroma_storage"
COLLECTION_NAME = "onboarding_docs"
    
def get_chroma_collection():
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    embedding_fn = embedding_functions.DefaultEmbeddingFunction()
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn
    )
    return collection

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()
    return full_text

def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        start = end - overlap
    return chunks

def ingest_all_pdfs():
    collection = get_chroma_collection()

    pdf_files = [f for f in os.listdir(DOCS_FOLDER) if f.endswith(".pdf")]

    if not pdf_files:
        print("Koi PDF nahi mili documents/ folder mein!")
        return

    total_chunks = 0

    for pdf_file in pdf_files:
        pdf_path = os.path.join(DOCS_FOLDER, pdf_file)
        print(f"Processing: {pdf_file}")

        text = extract_text_from_pdf(pdf_path)
        chunks = chunk_text(text)

        for i, chunk in enumerate(chunks):
            doc_id = f"{pdf_file}_chunk_{i}"
            collection.add(
                ids=[doc_id],
                documents=[chunk],
                metadatas=[{"source": pdf_file}]
            )

        print(f"  {len(chunks)} chunks added from {pdf_file}")
        total_chunks += len(chunks)

    print(f"\nDone! Total {total_chunks} chunks ChromaDB mein save ho gaye.")

def search_docs(query, n_results=3):
    collection = get_chroma_collection()
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    if not results["documents"][0]:
        return "Koi relevant document nahi mila."

    output = ""
    for i, doc in enumerate(results["documents"][0]):
        source = results["metadatas"][0][i]["source"]
        output += f"[{source}]\n{doc}\n\n"
    return output.strip()

if __name__ == "__main__":
    ingest_all_pdfs()