# StudyMate AI

An AI study assistant built with FastAPI and the Gemini API. It chats with students and remembers the conversation. Planned features: answering questions from PDFs (RAG), summarizing text, and generating quizzes.

## Status

- Milestone 1: project setup and a running FastAPI backend (done)
- Milestone 2: connected the Gemini model and added a `/chat` endpoint (done)
- Milestone 3: conversation memory with SQLite, multiple chats (done)
- Milestone 4: PDF assistant with RAG (in progress)

## Features so far

- Chat with an AI model through your own FastAPI server
- Conversation memory: every message is saved in SQLite and the history is sent to the model with each question
- Multiple separate conversations
- List and reopen past chats
- Error handling for unknown conversations (404) and model failures (502)

## Tech stack

- Python 3.12
- FastAPI and Uvicorn
- Google Gemini API (`google-genai` library)
- SQLite (built into Python)
- python-dotenv for secrets

## Project structure

```
studymate-ai/
├── backend/
│   ├── main.py              # FastAPI app and endpoints
│   ├── db/
│   │   └── database.py      # SQLite connection and table setup
│   └── services/
│       ├── llm_client.py    # Talks to the Gemini model
│       └── memory.py        # Saves and loads conversations
├── requirements.txt
├── .gitignore
└── README.md
```

## API endpoints

| Method | Endpoint | What it does |
|---|---|---|
| GET | `/` | Health check |
| POST | `/chat` | Send a message. Include `conversation_id` to continue a chat, or leave it out to start a new one |
| GET | `/conversations` | List all saved chats |
| GET | `/conversations/{conversation_id}` | Get all messages of one chat |

Example request body for `/chat`:

```json
{
  "message": "Explain what a variable is in Python",
  "conversation_id": 1
}
```

## How to run

1. Create a virtual environment: `python -m venv venv`
2. Activate it (Windows): `venv\Scripts\activate`
3. Install libraries: `pip install -r requirements.txt`
4. Create a `.env` file in the project folder with your own Gemini API key:
   ```
   GEMINI_API_KEY=your-key-here
   GEMINI_MODEL=your-model-id-here
   ```
   Get a free key at Google AI Studio and check the current model IDs in the Gemini API docs.
5. Start the server: `uvicorn backend.main:app --reload`
6. Open `http://127.0.0.1:8000/docs` to try the endpoints.

## How memory works

The model itself is stateless. On every `/chat` request the server saves the user's message, loads the full history of that conversation from SQLite, sends it to the model, and then saves the model's reply. Two tables are used: `conversations` and `messages`.

## Limitations

- No user accounts: anyone who can reach the server can read every chat
- Very long conversations are not trimmed yet, so they may exceed the model's input limit
- Free-tier API limits apply

## Roadmap

- PDF upload and question answering (RAG)
- Summarizer, study assistant (MCQs, notes) and code assistant
- Image understanding, web search and a Streamlit chat interface
