import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import faiss
import numpy as np
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Paths
CV_MD_PATH = "assets/maia_cv.md"

# FastAPI app
app = FastAPI(title="Maia CV Chatbot")

# Request model
class ChatRequest(BaseModel):
    message: str

# Load CV
if not Path(CV_MD_PATH).exists():
    raise FileNotFoundError(f"Markdown CV not found at {CV_MD_PATH}")

cv_text = Path(CV_MD_PATH).read_text(encoding="utf-8")

# --- Chunking function ---
def chunk_text(text, max_tokens=200):
    """Simple chunking by number of words (approximation for tokens)"""
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_tokens):
        chunk = " ".join(words[i:i+max_tokens])
        chunks.append(chunk)
    return chunks

cv_chunks = chunk_text(cv_text)

# --- Embeddings ---
embedding_dim = 1536  # text-embedding-3-small

def get_embedding(text: str):
    """Return embedding vector for a text"""
    resp = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return np.array(resp.data[0].embedding).astype("float32")

cv_embeddings = np.array([get_embedding(chunk) for chunk in cv_chunks])

# Build FAISS index
index = faiss.IndexFlatL2(embedding_dim)
index.add(cv_embeddings)

# --- Chat endpoint ---
@app.post("/chat")
async def chat(req: ChatRequest):
    query = req.message.strip()

    # --- Contact info rule ---
    contact_keywords = ["email", "phone", "contact", "reach", "linkedin"]
    if any(k.lower() in query.lower() for k in contact_keywords):
        return {"response": "Sorry, I cannot share personal contact details. You can connect with Maia on LinkedIn: https://uk.linkedin.com/in/maia-nagra and send a message there."}

    # --- Retrieve relevant chunk ---
    q_emb = np.array([get_embedding(query)])  # FIXED: no model argument here
    D, I = index.search(q_emb, k=2)  # retrieve top 2 similar chunks
    context = "\n\n".join([cv_chunks[i] for i in I[0]])

    # --- Construct prompt for GPT ---
    system_instruction = (
        "You are a CV assistant for Maia Nagra.\n"
        "- Answer questions ONLY about Maia's professional experience, skills, education, and highlights.\n"
        "- If the question is unrelated to the CV, politely say you can only answer questions about Maia."
    )
    prompt = f"{system_instruction}\n\nCV Context:\n{context}\n\nUser Question: {query}"

    # --- Generate response ---
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        answer = response.choices[0].message.content.strip()
        return {"response": answer}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Run app ---
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
