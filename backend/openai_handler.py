import os
from dotenv import load_dotenv
from openai import OpenAI
import json

# Load environment variables
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

# Fallback sentiment analysis (no API calls needed)
def simple_sentiment_analysis(text):
    """Simple keyword-based sentiment analysis as fallback"""
    text_lower = text.lower()
    
    positive_words = ["happy", "excited", "joyful", "great", "wonderful", "amazing", "love", "blessed", "grateful", "fantastic", "thrilled", "awesome", "good", "better", "best", "enjoyed", "beautiful", "perfect"]
    negative_words = ["sad", "depressed", "hurt", "lonely", "terrible", "awful", "anxious", "worried", "scared", "stressed", "angry", "frustrated", "bad", "worse", "worst", "hate", "pain", "tired"]
    calm_words = ["calm", "peaceful", "relaxed", "serene", "content", "zen", "chill", "meditate", "quiet", "rest", "sleep", "breathe"]
    excited_words = ["excited", "thrilled", "enthusiastic", "pumped", "energetic", "vibrant", "alive"]
    
    pos_count = sum(text_lower.count(w) for w in positive_words)
    neg_count = sum(text_lower.count(w) for w in negative_words)
    calm_count = sum(text_lower.count(w) for w in calm_words)
    exc_count = sum(text_lower.count(w) for w in excited_words)
    
    total = pos_count + neg_count + calm_count + exc_count
    
    if total == 0:
        return {
            "emotional_state": "neutral",
            "emotions": ["thoughtful", "reflective"],
            "themes": ["life experiences"],
            "insight": "Your memories show thoughtful reflection."
        }
    
    if pos_count > neg_count and pos_count > calm_count:
        state = "positive"
        emotions = ["happy", "grateful", "hopeful"]
    elif neg_count > pos_count:
        state = "negative"
        emotions = ["sad", "concerned", "thoughtful"]
    elif calm_count > pos_count:
        state = "calm"
        emotions = ["peaceful", "reflective", "serene"]
    else:
        state = "neutral"
        emotions = ["balanced", "thoughtful"]
    
    sentiment = int((pos_count / max(total, 1)) * 100)
    
    return {
        "emotional_state": state,
        "emotions": emotions,
        "themes": extract_themes(text),
        "insight": f"Your memories show a {state} emotional tone."
    }

def extract_themes(text):
    """Extract simple themes from text"""
    text_lower = text.lower()
    themes = []
    
    theme_keywords = {
        "work": ["work", "job", "office", "meeting", "project", "boss", "colleague"],
        "relationships": ["love", "friend", "family", "partner", "girlfriend", "boyfriend", "mother", "father", "sister", "brother"],
        "health": ["exercise", "gym", "workout", "healthy", "sick", "illness", "doctor", "health"],
        "learning": ["learn", "study", "school", "book", "course", "education", "knowledge"],
        "travel": ["trip", "travel", "visit", "vacation", "journey", "adventure", "explore"],
        "creativity": ["art", "music", "create", "design", "write", "draw", "painting"],
        "personal growth": ["growth", "improve", "challenge", "overcome", "achieve", "goal", "success"]
    }
    
    for theme, keywords in theme_keywords.items():
        if any(kw in text_lower for kw in keywords):
            themes.append(theme)
    
    return themes[:3] if themes else ["reflection"]

def analyze_feelings(memories_text):
    """Analyze user's feelings from their memories (with API fallback)"""
    # Try OpenAI first
    if client:
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an empathetic AI therapist. Analyze the user's memories and provide:
1. Overall emotional state (positive, negative, mixed, neutral)
2. Key emotions detected (list 3-5)
3. Main themes or patterns
4. A brief compassionate insight (1-2 sentences)

Format your response as JSON with keys: emotional_state, emotions, themes, insight"""
                    },
                    {
                        "role": "user",
                        "content": f"Please analyze these memories:\n\n{memories_text}"
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            result = response.choices[0].message.content
            try:
                analysis = json.loads(result)
            except:
                analysis = simple_sentiment_analysis(memories_text)
            
            return analysis
        
        except Exception as e:
            # Fall back to simple analysis if API fails
            if "quota" in str(e).lower() or "insufficient" in str(e).lower():
                return simple_sentiment_analysis(memories_text)
            raise
    
    # Use fallback if no API key
    return simple_sentiment_analysis(memories_text)


def chat_with_ai(user_message, memories_context=None, chat_history=None):
    """Chat with OpenAI (with smart fallback) - NO RECURSIVE LOOPS"""
    
    # Simple fallback response if no API
    simple_responses = {
        "how are you": "I'm here and listening to you. How are you feeling right now?",
        "hello": "Hello. I'm here to hear you and understand how you're feeling.",
        "hi": "Hi there. What's on your mind today?",
        "help": "I'm here to support you. Please share what you're thinking or feeling, and I'll try to understand.",
        "feel": "It's important to acknowledge your feelings. What emotions are coming up for you?",
        "memory": "Your memories are meaningful. Is there something you'd like to reflect on?",
        "sad": "I hear that you're sad, and that can be really heavy. Would you like to talk more about it?",
        "happy": "That sounds lovely. It's great that you're feeling good—tell me more if you'd like.",
        "thank": "You're welcome. I'm here whenever you need to share.",
        "default": "I appreciate you sharing that. Can you tell me more so I can understand better?"
    }
    
    if client:
        try:
            messages = [
                {
                    "role": "system",
                    "content": """You are a warm, empathetic AI companion who truly listens. Always acknowledge the user's emotions and respond as if you understand what it feels like to be in their situation. Keep responses concise (2-3 sentences), genuine, supportive, and understanding."""
                }
            ]
            
            # Add chat history - FIXED to prevent loops
            if chat_history and isinstance(chat_history, list):
                # Only add valid, non-empty messages from recent history
                for msg in chat_history[-3:]:  # Keep only last 3 messages
                    if isinstance(msg, dict):
                        role = msg.get("role", "").strip()
                        content = msg.get("content", "").strip()
                        
                        # Only add if both role and content are non-empty
                        if role in ["user", "assistant"] and content:
                            messages.append({
                                "role": role,
                                "content": content
                            })
            
            # Add current user message (always as user role)
            messages.append({
                "role": "user",
                "content": user_message.strip()
            })
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.8,
                max_tokens=300
            )
            
            text = response.choices[0].message.content.strip()
            # add a small empathetic prefix if user mentioned emotions
            if any(word in user_message.lower() for word in ["sad","happy","angry","anxious","depress","lonely","hurt"]):
                text = "I understand how that feels. " + text
            return text
        
        except Exception as e:
            error_str = str(e).lower()
            if "quota" in error_str or "insufficient" in error_str:
                # Use simple fallback on quota error
                msg_lower = user_message.lower()
                for key, response in simple_responses.items():
                    if key in msg_lower:
                        return response
                return simple_responses["default"]
            raise
    
    # No API key - use simple responses
    msg_lower = user_message.lower()
    for key, response in simple_responses.items():
        if key in msg_lower:
            return response
    return simple_responses["default"]


def generate_mood_report(memories_list):
    """Generate a detailed mood report (with fallback)"""
    
    memories_str = "\n".join(memories_list) if isinstance(memories_list, list) else str(memories_list)
    
    if client:
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a mood analysis expert. Generate a brief, warm report:
1. Overall mood tendency
2. Emotional patterns
3. Positive highlights
4. One encouraging message

Keep it supportive and non-judgmental."""
                    },
                    {
                        "role": "user",
                        "content": f"Please analyze my memories and create a mood report:\n\n{memories_str}"
                    }
                ],
                temperature=0.7,
                max_tokens=400
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            if "quota" in str(e).lower() or "insufficient" in str(e).lower():
                # Generate simple report
                analysis = simple_sentiment_analysis(memories_str)
                report = f"""
📊 **Your Mood Report** (Demo Mode)

**Overall Mood:** {analysis['emotional_state'].upper()}

**Key Emotions:** {', '.join(analysis['emotions'])}

**Themes in Your Memories:** {', '.join(analysis['themes'])}

**Insight:** {analysis['insight']}

💡 **Note:** Running in demo mode. For detailed AI analysis, please upgrade your OpenAI plan.
"""
                return report
            raise
    
    # Fallback report
    analysis = simple_sentiment_analysis(memories_str)
    report = f"""
📊 **Your Mood Report** (Demo Mode)

**Overall Mood:** {analysis['emotional_state'].upper()}

**Key Emotions:** {', '.join(analysis['emotions'])}

**Themes in Your Memories:** {', '.join(analysis['themes'])}

**Insight:** {analysis['insight']}

💡 **Note:** Using demo analysis. Upgrade your OpenAI plan for advanced AI features.
"""
    return report

