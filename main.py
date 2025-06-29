from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
import requests
from dotenv import load_dotenv
from rag_engine import query_collection  # <-- uses shared knowledge base

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="FinSolve RBAC Chatbot")

# Enable CORS for frontend (Streamlit)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request body schema
class QueryPayload(BaseModel):
    user: str
    role: str
    query: str

@app.get("/")
def read_root():
    return {"message": "Welcome to FinSolve RBAC Chatbot API!"}

@app.post("/query")
def handle_query(payload: QueryPayload):
    role = payload.role.lower()
    query = payload.query.strip()

    # Get relevant context from the RBAC-aware function
    results = query_collection(role, query)
    context_chunks = results.get("documents", [[]])[0]

    if not context_chunks:
        return {"response": "No relevant information found for your role."}

    context = "\n".join(context_chunks)

    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    if not openrouter_api_key:
        return {"response": "API key not configured."}

    headers = {
        "Authorization": f"Bearer {openrouter_api_key}",
        "HTTP-Referer": "https://finsolve.com",
        "X-Title": "FinSolve AI Chatbot"
    }

    data = {
        "model": "deepseek/deepseek-r1-0528:free",
        "messages": [
            {"role": "system", "content": f"You are a helpful assistant for the {role} team."},
            {"role": "user", "content": f"{query}\n\nContext:\n{context}"}
        ]
    }

    print("🧠 Context used:", context)
    print("🚀 Sending request to LLM...")

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)

    if response.status_code == 200:
        return {"response": response.json()["choices"][0]["message"]["content"]}
    else:
        return {"response": f"LLM error ({response.status_code}): {response.text}"}
