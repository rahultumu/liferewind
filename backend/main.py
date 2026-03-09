from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import shutil
import time
from datetime import datetime, timedelta
import json
from pathlib import Path

from speech_to_text import transcribe_audio
from image_analysis import analyze_image
from embedding import create_embedding
from database import add_memory, search_memory
from memory_store import log_memory, get_memory_logs
from openai_handler import chat_with_ai, analyze_feelings, generate_mood_report
from supabase_db import add_memory as supabase_add, get_memories, get_memory_by_date, get_all_memory_texts, get_memory_stats, import_from_json


app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/add_text_memory")
def add_text_memory(
    text: str = Form(...),
    email: str = Form(None),
    date: str = Form(None)
):
    """Store a text memory, optionally tagging it with a specific date."""
    try:
        # local indexing and logging
        embedding = create_embedding(text)
        add_memory(embedding, text)
        log_memory({"type": "text", "content": text})
        
        status = "local"
        if email:
            metadata = {"date": date} if date else None
            res = supabase_add(email, text, memory_type="text", metadata=metadata)
            if res.get("status") == "success":
                status = "supabase"
        return {"status": "memory stored", "storage": status}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/add_voice_memory")
def add_voice_memory(file: UploadFile = File(...)):
    try:
        path = f"uploads/audio/{file.filename}"
        with open(path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        text = transcribe_audio(path)
        embedding = create_embedding(text)
        add_memory(embedding, text)
        log_memory({"type": "voice", "filename": file.filename, "transcription": text})
        
        return {"transcription": text, "status": "success"}
    except Exception as e:
        return {"transcription": "", "status": "error", "message": str(e)}


@app.post("/add_image_memory")
def add_image_memory(file: UploadFile = File(...)):
    try:
        path = f"uploads/images/{file.filename}"
        with open(path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        description = analyze_image(path)
        embedding = create_embedding(description)
        add_memory(embedding, description)
        log_memory({"type": "image", "filename": file.filename, "description": description})
        
        return {"description": description, "status": "success"}
    except Exception as e:
        return {"description": "", "status": "error", "message": str(e)}


@app.get("/search")
def search_memories(query: str):
    embedding = create_embedding(query)
    results = search_memory(embedding)
    return {"results": results}

@app.get("/export_from_json")
def export_from_json(email: str = None):
    """Import existing memories from local JSON into Supabase."""
    try:
        path = "vector_db/memories.json"
        res = import_from_json(path, user_email=email)
        return res
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/memories_by_date")
def get_memories_by_date(date: str, email: str = None):
    """Get all memories from a specific date (YYYY-MM-DD format)"""
    try:
        if email:
            results = get_memory_by_date(email, date)
            return {"memories": results, "date": date}
        logs = get_memory_logs()
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
        
        memories_on_date = []
        for log in logs:
            log_timestamp = datetime.fromisoformat(log["timestamp"])
            log_date = log_timestamp.date()
            
            if log_date == target_date:
                memories_on_date.append({
                    "content": format_memory_content(log["data"]),
                    "timestamp": log_timestamp.strftime("%H:%M:%S"),
                    "type": log["data"].get("type", "unknown")
                })
        
        return {"memories": memories_on_date, "date": date}
    except Exception as e:
        return {"error": str(e), "memories": []}

@app.get("/memory_stats")
def get_memory_stats(email: str = None):
    """Get statistics about stored memories"""
    try:
        if email:
            stats = get_memory_stats(email)
            return stats
        logs = get_memory_logs()
        
        total_memories = len(logs)
        
        # Count unique dates with memories
        dates_with_memories = set()
        for log in logs:
            log_timestamp = datetime.fromisoformat(log["timestamp"])
            dates_with_memories.add(log_timestamp.date())
        
        return {
            "total_memories": total_memories,
            "days_with_memories": len(dates_with_memories)
        }
    except Exception as e:
        return {"total_memories": 0, "days_with_memories": 0, "error": str(e)}

def format_memory_content(data):
    """Format memory data for display"""
    memory_type = data.get("type", "unknown")
    
    if memory_type == "text":
        return data.get("content", "No content")
    elif memory_type == "voice":
        return f"🎤 Voice: {data.get('transcription', 'No transcription')}"
    elif memory_type == "image":
        return f"🖼️ Image: {data.get('description', 'No description')}"
    else:
        return str(data)

@app.get("/analyze_mood")
def analyze_mood():
    """Analyze user's mood based on stored memories"""
    try:
        logs = get_memory_logs()
        
        if not logs:
            return {
                "mood": "neutral",
                "sentiment": 0,
                "analysis": "No memories found. Start adding memories to analyze your mood.",
                "keywords": []
            }
        
        # Extract all memory content
        all_content = []
        for log in logs:
            content = format_memory_content(log["data"])
            all_content.append(content)
        
        combined_text = " ".join(all_content).lower()
        
        # Simple emotion detection based on keywords
        emotions = {
            "happy": ["happy", "excited", "joyful", "great", "wonderful", "amazing", "love", "laughing", "blessed", "grateful"],
            "sad": ["sad", "depressed", "down", "unhappy", "crying", "hurt", "lonely", "lost", "terrible", "awful"],
            "anxious": ["anxious", "worried", "stressed", "nervous", "afraid", "panic", "scared", "unsure", "overwhelmed"],
            "excited": ["excited", "thrilled", "exhilarating", "pump", "amazing", "fantastic", "incredible"],
            "calm": ["calm", "peaceful", "relaxed", "serene", "quiet", "content", "zen", "chill"]
        }
        
        emotion_scores = {mood: 0 for mood in emotions}
        
        for emotion, keywords in emotions.items():
            for keyword in keywords:
                emotion_scores[emotion] += combined_text.count(keyword)
        
        # Determine primary mood
        primary_mood = max(emotion_scores, key=emotion_scores.get)
        if emotion_scores[primary_mood] == 0:
            primary_mood = "neutral"
        
        # Calculate sentiment percentage
        positive_words = ["happy", "love", "great", "wonderful", "amazing", "blessed", "grateful", "excited", "thrilled"]
        negative_words = ["sad", "depressed", "hurt", "lonely", "terrible", "awful", "anxious", "worried", "scared"]
        
        positive_count = sum(combined_text.count(w) for w in positive_words)
        negative_count = sum(combined_text.count(w) for w in negative_words)
        total_emotion_words = positive_count + negative_count
        
        if total_emotion_words > 0:
            sentiment_score = int((positive_count / total_emotion_words) * 100)
        else:
            sentiment_score = 50
        
        # Get top keywords
        top_emotions = sorted(emotion_scores.items(), key=lambda x: x[1], reverse=True)
        keywords = [f"{mood}: {score} mentions" for mood, score in top_emotions[:3] if score > 0]
        
        # Create analysis message
        analysis_messages = {
            "happy": "😊 Your memories show a lot of positivity and joy!",
            "sad": "😔 Your memories suggest you've been going through some challenging times.",
            "anxious": "😰 Your memories indicate some stress and worries.",
            "excited": "🤗 Your memories are full of excitement and enthusiasm!",
            "calm": "😌 Your memories reflect a peaceful and composed state.",
            "neutral": "😐 Your memories have a balanced emotional tone."
        }
        
        analysis = analysis_messages.get(primary_mood, "Your emotional state is balanced.")
        
        return {
            "mood": primary_mood,
            "sentiment": sentiment_score,
            "analysis": analysis,
            "keywords": keywords
        }
    except Exception as e:
        return {
            "mood": "error",
            "sentiment": 0,
            "analysis": f"Error analyzing mood: {str(e)}",
            "keywords": []
        }


@app.post("/chat")
def handle_chat(request_body: dict):
    """Chat with AI powered by OpenAI ChatGPT, with memory context"""
    try:
        message = request_body.get("message", "").strip()
        
        if not message:
            return {
                "response": "Hi there! I'm here to listen. What's on your mind?",
                "status": "success"
            }
        
        logs = get_memory_logs()
        
        # Get recent relevant memories for context
        try:
            message_embedding = create_embedding(message)
            relevant_memories = search_memory(message_embedding, k=3)
            memories_context = "\n".join(relevant_memories) if relevant_memories else None
        except:
            memories_context = None
        
        # Get chat history from request
        chat_history = request_body.get("history", [])
        
        # Get response from OpenAI
        ai_response = chat_with_ai(message, memories_context=memories_context, chat_history=chat_history)
        
        # simple motivational suggestion based on keywords
        lower = message.lower()
        negatives = ["sad","depress","unhappy","hurt","lonely","angry","stress","anxious"]
        if any(word in lower for word in negatives):
            ai_response += "\n\n💡 *Remember, you're not alone – reach out, take a deep breath, and keep moving forward. You've got this!*"
        
        return {
            "response": ai_response,
            "status": "success"
        }
    
    except Exception as e:
        return {
            "response": "I'm here to listen and support you. What's on your mind?",
            "status": "error",
            "message": str(e)
        }


@app.get("/analyze_feelings")
def get_feelings_analysis():
    """Analyze user's feelings from all stored memories using GPT"""
    try:
        logs = get_memory_logs()
        
        if not logs:
            return {
                "analysis": {
                    "emotional_state": "neutral",
                    "emotions": ["reflective"],
                    "themes": ["new user"],
                    "insight": "Start adding memories to get personalized feeling analysis."
                },
                "status": "success"
            }
        
        # Combine all memory content
        all_memories = []
        for log in logs:
            content = format_memory_content(log["data"])
            all_memories.append(content)
        
        memories_text = "\n".join(all_memories)
        
        # Analyze using OpenAI
        analysis = analyze_feelings(memories_text)
        
        return {
            "analysis": analysis,
            "status": "success"
        }
    
    except Exception as e:
        return {
            "analysis": {"error": str(e)},
            "status": "error"
        }


@app.get("/mood_report")
def generate_user_mood_report():
    """Generate a detailed mood report from all memories"""
    try:
        logs = get_memory_logs()
        
        if not logs:
            return {
                "report": "No memories found. Start adding memories to generate a mood report.",
                "status": "success"
            }
        
        # Extract all memory content
        all_memories = []
        for log in logs:
            content = format_memory_content(log["data"])
            all_memories.append(content)
        
        # Generate report using OpenAI
        report = generate_mood_report(all_memories)
        
        return {
            "report": report,
            "status": "success"
        }
    
    except Exception as e:
        return {
            "report": f"Unable to generate report: {str(e)}",
            "status": "error"
        }


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
