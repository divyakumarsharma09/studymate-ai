# StudyMate AI

An AI study assistant for students, built with FastAPI, Streamlit and the Gemini API. It chats and remembers the conversation, answers questions from uploaded PDFs (RAG), summarizes text, creates revision notes and exam questions, and runs interactive multiple-choice quizzes.

## Status

- Milestone 1: project setup and FastAPI backend (done)
- Milestone 2: Gemini chatbot with a `/chat` endpoint (done)
- Milestone 3: conversation memory with SQLite and multiple chats (done)
- Milestone 4: PDF assistant with RAG (done)
- Milestone 5: summarizer, study assistant and quiz (done)
- Milestone 6: Streamlit chat interface (done)
- Next: testing and evaluation, then deployment

## Features

- Chat with an AI model, with memory: every message is saved in SQLite and the history is sent to the model with each question
- Multiple conversations that can be listed and reopened
- Upload a PDF and ask questions about it (RAG with Gemini embeddings and ChromaDB)
- Answers use only the uploaded document and say so when the answer is not in it
- Summaries in three lengths from pasted text or a PDF
- Study modes: simple explanation, revision notes, short and long exam questions
- Multiple-choice quiz returned as validated JSON, with shuffled options, automatic checking and a score
- Streamlit interface with Chat, PDF assistant and Study tools pages

## Tech stack

- Python 3.12
- FastAPI and Uvicorn (backend API)
- Streamlit (interface)
- Google Gemini API through the `google-genai` library (chat, study tools, embeddings)
- ChromaDB (vector database) and PyMuPDF (PDF text extraction)
- SQLite (conversations, built into Python)
- Pydantic (input and output validation)

## How it works

```
Streamlit interface  ->  FastAPI backend  ->  Gemini API
                                         ->  SQLite (conversations)
                                         ->  ChromaDB (PDF chunks and embeddings)
```

**Chat memory:** the model is stateless. On every `/chat` request the backend saves the user's message, loads the full history of that conversation from SQLite, sends it to the model, and saves the reply.

**PDF question answering (RAG):** PDF text is extracted page by page, split into overlapping chunks, embedded with Gemini, and stored in ChromaDB with the page number. For a question, the 4 most similar chunks are retrieved and put into a prompt that tells the model to answer only from them.

**Quiz:** the model is asked to return JSON in a fixed shape. The backend validates it with Pydantic, retries once if it is invalid, and shuffles the options.

## Project structure

```
studymate-ai/
├── backend/
│   ├── main.py                 # FastAPI app and endpoints
│   ├── db/
│   │   └── database.py         # SQLite connection and tables
│   ├── rag/
│   │   ├── pdf_reader.py       # extracts text per page
│   │   ├── chunker.py          # splits text into overlapping chunks
│   │   ├── embedder.py         # creates embeddings with Gemini
│   │   ├── vector_store.py     # stores and searches chunks in ChromaDB
│   │   └── qa.py               # builds the prompt and answers from a PDF
│   ├── routes/
│   │   └── study_routes.py     # /study and /quiz endpoints
│   └── services/
│       ├── llm_client.py       # talks to the Gemini model
│       ├── memory.py           # saves and loads conversations
│       ├── study.py            # summary and study prompts
│       └── quiz.py             # quiz generation and validation
├── frontend/
│   ├── app.py                  # page navigation
│   ├── api_client.py           # calls the backend
│   ├── chat_view.py            # chat page
│   ├── pdf_view.py             # PDF assistant page
│   └── study_view.py           # summary, study modes and quiz
├── requirements.txt
├── .gitignore
└── README.md
```

## API endpoints

| Method | Endpoint | What it does |
|---|---|---|
| GET | `/` | Health check |
| POST | `/chat` | Send a message. Include `conversation_id` to continue a chat |
| GET | `/conversations` | List saved chats |
| GET | `/conversations/{conversation_id}` | Get all messages of one chat |
| POST | `/upload-pdf` | Upload a PDF. Returns a `doc_id` |
| GET | `/documents` | List uploaded PDFs |
| POST | `/ask-pdf` | Ask a question about a PDF using its `doc_id` |
| POST | `/summarize` | Summarize text or a PDF (short, medium or detailed) |
| POST | `/study` | Explain, revision notes, short or long questions from a topic, text or PDF |
| POST | `/quiz` | Generate a multiple-choice quiz from a topic, text or PDF |

## How to run

1. Create a virtual environment: `python -m venv venv`
2. Activate it (Windows): `venv\Scripts\activate`
3. Install libraries: `pip install -r requirements.txt`
4. Create a `.env` file in the project folder with your own values:
   ```
   GEMINI_API_KEY=your-key-here
   GEMINI_MODEL=your-model-id-here
   GEMINI_EMBED_MODEL=gemini-embedding-001
   ```
   Get a free key in Google AI Studio and check the current model IDs in the Gemini API docs.
5. Start the backend in one terminal: `uvicorn backend.main:app --reload`
6. Start the interface in a second terminal: `streamlit run frontend/app.py`
7. Open `http://localhost:8501`. The API docs are at `http://127.0.0.1:8000/docs`.

## Limitations

- No user accounts: anyone who can reach the server can read every chat and document
- Scanned PDFs (images only) are not supported yet
- Very long conversations are not trimmed yet, so they may exceed the model's input limit
- AI-generated answers, questions and quiz answers can contain mistakes and should be checked
- PDF and chat text is sent to Google, so do not use private documents on the free tier
- Free-tier API limits apply

## Roadmap

- Testing and evaluation (accuracy, hallucination, retrieval quality, response time)
- Deployment
- Image understanding, web search and voice input
