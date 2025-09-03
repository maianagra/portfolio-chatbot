# Maia's CV Chatbot

A FastAPI-based chatbot that answers questions about Maia Nagra’s CV.  
It retrieves relevant context from a Markdown CV, uses OpenAI embeddings + GPT-4o-mini, and responds to user queries.  
The bot also enforces rules for sensitive information and unrelated questions.


## Features

- Answers questions **only** about Maia's professional experience, skills, education, and highlights.  
- Detects requests for personal contact info and responds with a LinkedIn fallback.  
- Uses **FAISS** for semantic search on the Markdown CV.  
- Powered by **OpenAI GPT** and embeddings for context-aware answers.  


## Project Structure

```
portfolio-chatbot/
│
├─ assets/
│ └─ maia_cv.md # Your CV in Markdown format
│
├─ scripts/
│ └─ pdf_to_md.py # Script to convert PDF CV to Markdown
│
├─ main.py # FastAPI application
├─ requirements.txt
└─ README.md
```

## Pre-requisites

Before running this project, make sure you have:

- **Python 3.11+** installed  
- **OpenAI API Key**

## Local Setup

### 1. Clone the repo

```
git clone <your-repo-url>
cd portfolio-chatbot
```

### 2. Create a virtual environment
```
python3 -m venv venv
source venv/bin/activate       # Linux/macOS
# or
venv\Scripts\activate          # Windows
```

### 3. Install dependencies
```
pip install -r requirements.txt
```

### 4. Add your OpenAI API key
```
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
```

## Running the Chatbot
```
python -m uvicorn main:app --reload
```
This starts the FastAPI server at http://127.0.0.1:8000.

The /chat endpoint accepts POST requests with a JSON body:

```
{
  "message": "Your question here"
}
```

## Example cURL Requests
Ask about professional experience
```
curl -X POST "http://127.0.0.1:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Can you tell me about Maia’s front-end experience?"}'
```

Ask about education
```
curl -X POST "http://127.0.0.1:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Where did Maia go to university and what did she study?"}'
```

Ask unrelated questions
```
curl -X POST "http://127.0.0.1:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "What is Maia’s favorite food?"}'
```

Ask for contact info
```
curl -X POST "http://127.0.0.1:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Can you give me Maia’s email or phone number?"}'
```