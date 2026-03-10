# AI Life Rewind 🧠

Your Personal Memory Search Engine powered by AI

## 📋 Overview

AI Life Rewind is a web application that lets you store memories (text, voice, images) and search them semantically like Google for your life. 

### Example Queries:
- "When did I meet Rahul?"
- "Show my meetings last week"
- "When did I go to the beach?"

## 🏗 System Architecture

```
User → Upload Memory
   ↓
FastAPI Backend
   ↓
AI Processing
   ├── Whisper (speech → text)
   ├── OpenCV (image understanding)
   └── OpenAI Embeddings
   ↓
FAISS Vector Database
   ↓
Semantic Search
   ↓
Timeline UI
```

## 📂 Project Structure

```
ai-life-rewind/
├── backend/
│   ├── main.py              # FastAPI server
│   ├── memory_store.py      # Memory logging utility
│   ├── embedding.py         # OpenAI embeddings
│   ├── speech_to_text.py    # Whisper transcription
│   ├── image_analysis.py    # Image processing
│   └── database.py          # FAISS vector DB
├── frontend/
│   └── app.py              # Streamlit UI
├── uploads/
│   ├── images/
│   └── audio/
├── vector_db/
│   └── faiss_index
├── requirements.txt
└── README.md
```

## 📦 Installation

### Prerequisites
- Python 3.8+
- OpenAI API Key
- pip

### Setup

1. **Clone/Create project:**
   ```bash
   cd ai-life-rewind
   ```

2. **Create virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables:**
   ```bash
   export OPENAI_API_KEY=your_api_key_here  # On Windows: set OPENAI_API_KEY=your_api_key_here
   ```

## ⚙️ Components

### Backend Modules

#### `embedding.py`
Creates vector embeddings for text using OpenAI's text-embedding-3-small model.

#### `speech_to_text.py`
Converts audio files to text using OpenAI's Whisper model.

#### `image_analysis.py`
Analyzes images and generates descriptions (can be enhanced with BLIP or GPT Vision).

#### `database.py`
Manages FAISS vector database for semantic search across memories.

#### `memory_store.py`
Logs all memories with timestamps for future retrieval and filtering.

### Frontend

Streamlit-based UI with sections for:
- Adding text memories
- Uploading and analyzing images
- Recording/uploading voice notes
- Semantic search across all memories

## 🚀 Running the Application

### ⛳ Deploying to Vercel
To deploy the backend on Vercel you need a FastAPI entrypoint at the repo root. A simple wrapper has been provided:

```python
# app.py (root of project)
from backend.main import app
```

Vercel will automatically detect `app.py` (or `main.py` – the latter was added as an extra fallback) and use the `app` instance. Additionally we have added a minimal `pyproject.toml` with an `app` script that points at the same object; this satisfies Vercel’s entrypoint check when it scans for a poetry project. The TOML now includes a PEP 621 `[project]` table so that `uv lock` (used in the build) can parse it without complaining about a missing `project` table.

Make sure you do **not** commit any secret keys (the `.env` file is now ignored).

If you still see "no fastapi entrypoint found" during deployment, verify that:
1. `app.py` or `main.py` is at the project root and contains `from backend.main import app`.
2. `pyproject.toml` exists with `[tool.poetry.scripts]` entry `app = "app:app"`.
3. You have a valid `vercel.json` file pointing the build at `app.py`.
4. The correct branch/folder is selected in your Vercel project settings.
5. Clear Vercel’s build cache or remove/re‑create the project if it continues to use old configuration.

A sample `vercel.json`:
```json
{
  "version": 2,
  "builds": [
    { "src": "app.py", "use": "@vercel/python" }
  ],
  "routes": [
    { "src": "\/(.*)", "dest": "app.py" }
  ]
}
```


## 🗄️ Optional Supabase Integration
To store memories in a hosted PostgreSQL database via Supabase, follow these steps:

1. Create a Supabase project and copy the **Project URL** and **Service Role Key**.
2. In the `backend` folder create or update a `.env` file with:
   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_SERVICE_KEY=eyJ...your_service_role_key...
   # optionally add the database connection string for automatic table creation
   SUPABASE_DB_URL=postgresql://postgres:your-db-password@db.your-project.supabase.co:5432/postgres
   ```
3. Use the Supabase dashboard SQL editor (or set `SUPABASE_DB_URL` above) to create two tables:
   ```sql
   create table if not exists memories (
     id bigserial primary key,
     user_email text,
     content text,
     type text,
     metadata jsonb,
     created_at timestamp
   );
   create table if not exists users (
     id bigserial primary key,
     email text unique,
     phone text,
     password text,
     created_at timestamp
   );
   ```
4. The backend will automatically connect using the REST API. When adding a text
   memory you can pass your email and the memory will be stored in Supabase.
5. To migrate existing local JSON memories, visit the home page and click
   **Import from JSON** (Supabase must be configured and tables created first).

The Supabase integration is optional; the app still works with the local FAISS
index if you don't set the environment variables.

# 🚀 Running the Application

### Terminal 1: Start Backend
```bash
cd backend
uvicorn main:app --reload
```
Backend runs at: `http://127.0.0.1:8000`

### Terminal 2: Start Frontend
```bash
cd frontend
streamlit run app.py
```
Frontend runs at: `http://localhost:8501`

## 🎯 Demo Script

**Calendar feelings:** in calendar view you can select a date, view memories, and write down your emotions or mood for that day.

**Motivational chat:** the AI will automatically offer encouraging suggestions if your message mentions stress, sadness, or other negative feelings.


1. **Add Text Memory:**
   - Go to "Add Text Memory"
   - Type: "Met Rahul at beach"
   - Click "Save Memory"

2. **Upload Image Memory:**
   - Go to "Upload Image"
   - Upload any image
   - Description is auto-generated and stored

3. **Upload Voice Memory:**
   - Go to "Upload Voice"
   - Upload an audio file
   - Transcription is auto-generated and stored

4. **Search Memories:**
   - Go to "Search Memories"
   - Query: "When did I meet Rahul?"
   - AI retrieves relevant memories semantically

## 🔑 Key Features

✅ **Multi-modal Memory Storage** - Text, Voice, Images
✅ **Semantic Search** - Find memories by meaning, not keywords
✅ **AI-Powered** - Automatic transcription and image analysis
✅ **Vector Database** - Fast similarity search with FAISS
✅ **Timeline View** - See memories organized chronologically
✅ **Simple UI** - Intuitive Streamlit interface

## 🎓 Hackathon Enhancements

### Future Improvements

1. **Enhanced Image Understanding**
   - Use BLIP for better image captions
   - Integrate GPT Vision for detailed analysis
   - Object detection and scene understanding

2. **Advanced Timeline Features**
   - Calendar view of memories
   - Time-based filtering
   - Memory clustering by themes

3. **Persistence**
   - Save FAISS index to disk
   - Database integration (PostgreSQL, MongoDB)
   - Cloud storage for files

4. **Social Features**
   - Share memory collections
   - Collaborate on memories
   - Public/private memory management

5. **Mobile Support**
   - React Native app
   - Offline memory capture
   - Background sync

6. **Analytics**
   - Memory statistics
   - Most searched topics
   - Memory trends over time

## 🛠 Tech Stack

- **Backend**: FastAPI, Python 3.8+
- **Frontend**: Streamlit
- **AI Models**: OpenAI (Embeddings + Whisper)
- **Vector DB**: FAISS
- **Image Processing**: OpenCV, PIL
- **Async**: asyncio

## 📝 API Endpoints

- `POST /add_text_memory` - Store text memory
- `POST /add_voice_memory` - Store voice memory with transcription
- `POST /add_image_memory` - Store image memory with description
- `GET /search` - Semantic search across memories
- `GET /health` - Health check

## 🐛 Troubleshooting

**CORS Issues:**
- Already handled in main.py with CORSMiddleware

**API Key Not Found:**
- Ensure `OPENAI_API_KEY` environment variable is set

**FAISS Import Error:**
- Run: `pip install faiss-cpu` (or `faiss-gpu` for GPU support)

**Audio Processing Issues:**
- Ensure ffmpeg is installed: `brew install ffmpeg` (macOS) or appropriate package manager

## 📄 License

Open source for hackathon and educational purposes.

## 🚀 Getting Started

```bash
# Install all dependencies
pip install -r requirements.txt

# Terminal 1: Run backend
cd backend && uvicorn main:app --reload

# Terminal 2: Run frontend  
cd frontend && streamlit run app.py

# Visit http://localhost:8501 in your browser
```

Happy remembering! 🎉
