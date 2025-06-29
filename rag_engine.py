# rag_engine.py
from chromadb import Client
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from typing import List, Dict
from dotenv import load_dotenv
import os

# Role-based access control
ROLE_ACCESS = {
    "employee": ["employee"],
    "hr": ["hr", "employee"],
    "engineering": ["engineering", "employee"],
    "marketing": ["marketing", "employee"],
    "finance": ["finance", "employee"],
    "c-level": ["finance", "hr", "engineering", "marketing", "employee"]
}

# Configure ChromaDB
CHROMA_DB_PERSIST_PATH = "./chroma_db_data"
EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=EMBEDDING_MODEL_NAME
)

client = Client(Settings(
    is_persistent=True,
    persist_directory=CHROMA_DB_PERSIST_PATH
))

def get_or_create_collection():
    return client.get_or_create_collection(
        name="finsolve_knowledge_base",
        embedding_function=embedding_fn
    )

def add_documents_to_collection(documents: List[str], metadatas: List[Dict], start_idx: int = 0):
    collection = get_or_create_collection()
    ids = [f"doc_{i + start_idx}" for i in range(len(documents))]
    
    if len(documents) != len(metadatas):
        raise ValueError("Document and metadata count must match.")

    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    print(f"✅ Added {len(documents)} documents to 'finsolve_knowledge_base'.")

def query_collection(role: str, query: str, k: int = 3):
    role = role.lower()
    allowed_types = ROLE_ACCESS.get(role, ["employee"])

    collection = get_or_create_collection()

    results = collection.query(
        query_texts=[query],
        n_results=k,
        where={"data_type": {"$in": allowed_types}},
        include=['documents', 'metadatas']  # ✅ Corrected from 'metadata'
    )

    print(f"🔍 Role: {role}")
    print(f"📌 Allowed: {allowed_types}")
    print(f"📄 Results: {results.get('documents', [[]])[0]}")

    return results
