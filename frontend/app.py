import streamlit as st
import requests
from datetime import datetime, date
import json
from pathlib import Path

API = "http://127.0.0.1:8000"

st.set_page_config(page_title="AI Life Rewind", layout="centered", initial_sidebar_state="collapsed")

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "login"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "user_phone" not in st.session_state:
    st.session_state.user_phone = None

# User storage file
USERS_FILE = Path("users.json")

def load_users():
    """Load users from file"""
    if USERS_FILE.exists():
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    """Save users to file"""
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

def user_exists(email):
    """Check if user exists"""
    users = load_users()
    return email in users

def register_user(email, phone, password):
    """Register new user"""
    users = load_users()
    if email in users:
        return False, "Email already registered"
    users[email] = {"phone": phone, "password": password}
    save_users(users)
    return True, "Signup successful!"

def verify_user(email, password):
    """Verify user login"""
    users = load_users()
    if email not in users:
        return False, "Email not registered"
    if users[email]["password"] != password:
        return False, "Incorrect password"
    return True, users[email]["phone"]

def logout():
    """Logout user"""
    st.session_state.user_email = None
    st.session_state.user_phone = None
    st.session_state.page = "login"
    st.rerun()

# LOGIN PAGE
if st.session_state.page == "login":
    st.markdown("# 🧠 AI Life Rewind")
    st.markdown("---")
    st.markdown("## Login to Your Account")
    st.markdown("")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 👤 Login")
        
        email = st.text_input("Email", placeholder="your@email.com", key="login_email")
        password = st.text_input("Password", type="password", placeholder="Enter password", key="login_password")
        
        if st.button("Sign In", use_container_width=True, key="btn_signin"):
            if email and password:
                success, phone_or_msg = verify_user(email, password)
                if success:
                    st.session_state.user_email = email
                    st.session_state.user_phone = phone_or_msg
                    st.session_state.page = "home"
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error(phone_or_msg)
            else:
                st.warning("Please fill in all fields")
    
    with col2:
        st.markdown("### 📝 New User?")
        st.markdown("")
        
        if st.button("Create Account", use_container_width=True, key="btn_signup_nav"):
            st.session_state.page = "signup"
            st.rerun()
        
        st.markdown("")
        st.info("Sign up to get started with AI Life Rewind")

# SIGNUP PAGE
elif st.session_state.page == "signup":
    st.markdown("# 🧠 AI Life Rewind")
    st.markdown("---")
    st.markdown("## Create Your Account")
    st.markdown("")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📝 Sign Up")
        
        email = st.text_input("Email", placeholder="your@email.com", key="signup_email")
        phone = st.text_input("Phone Number", placeholder="+1 (555) 000-0000", key="signup_phone")
        password = st.text_input("Password", type="password", placeholder="Create password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm password", key="confirm_password")
        
        if st.button("Sign Up", use_container_width=True, key="btn_register"):
            if not all([email, phone, password, confirm_password]):
                st.warning("Please fill in all fields")
            elif password != confirm_password:
                st.error("Passwords do not match")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters")
            else:
                success, message = register_user(email, phone, password)
                if success:
                    st.success("✅ Account created! Redirecting to login...")
                    st.session_state.page = "login"
                    st.rerun()
                else:
                    st.error(message)
    
    with col2:
        st.markdown("### 👤 Already have account?")
        st.markdown("")
        
        if st.button("Back to Login", use_container_width=True, key="btn_login_nav"):
            st.session_state.page = "login"
            st.rerun()
        
        st.markdown("")
        st.info("Login with your existing credentials")

# HOME PAGE
elif st.session_state.page == "home":
    # Header with user info and logout
    col_header1, col_header2, col_header3 = st.columns([2, 2, 1])
    
    with col_header1:
        st.markdown(f"**👤 {st.session_state.user_email}**")
    
    with col_header2:
        st.markdown(f"📱 {st.session_state.user_phone}")
    
    with col_header3:
        if st.button("Logout", use_container_width=True, key="btn_logout"):
            logout()
    
    st.markdown("---")
    
    st.markdown("# 🧠 AI Life Rewind")
    st.markdown("## Your Personal Memory Search Engine")
    st.markdown("---")
    
    # Current date display
    today = datetime.now()
    st.markdown(f"**Today:** {today.strftime('%A, %B %d, %Y')}")
    st.markdown("")
    
    # Menu options
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📝 Add Text Memory", use_container_width=True, key="btn_text"):
            st.session_state.page = "text_memory"
            st.rerun()
        
        if st.button("🖼️ Add Image", use_container_width=True, key="btn_image"):
            st.session_state.page = "image_memory"
            st.rerun()
    
    with col2:
        if st.button("🎤 Add Voice Note", use_container_width=True, key="btn_voice"):
            st.session_state.page = "voice_memory"
            st.rerun()
        
        if st.button("📅 Calendar View", use_container_width=True, key="btn_calendar"):
            st.session_state.page = "calendar"
            st.rerun()
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔍 Search Memories", use_container_width=True, key="btn_search"):
            st.session_state.page = "search"
            st.rerun()
    
    with col2:
        if st.button("💬 Chat with AI", use_container_width=True, key="btn_chat"):
            st.session_state.page = "chatbot"
            st.rerun()
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💭 Analyze Feelings", use_container_width=True, key="btn_home_analyze"):
            try:
                with st.spinner("Analyzing your emotions..."):
                    response = requests.get(f"{API}/analyze_feelings")
                
                if response.status_code == 200:
                    analysis = response.json().get("analysis", {})
                    st.markdown("### 📊 Your Feelings Analysis")
                    st.write(f"**Emotional State:** {analysis.get('emotional_state', 'N/A')}")
                    st.write(f"**Emotions:** {', '.join(analysis.get('emotions', []))}")
                    st.write(f"**Themes:** {', '.join(analysis.get('themes', []))}")
                    st.success(f"💡 {analysis.get('insight', '')}")
            except Exception as e:
                st.warning(f"Demo mode: Running simple analysis")
    
    with col2:
        if st.button("📈 Generate Mood Report", use_container_width=True, key="btn_home_report"):
            try:
                with st.spinner("Generating your mood report..."):
                    response = requests.get(f"{API}/mood_report")
                
                if response.status_code == 200:
                    report = response.json().get("report", "")
                    st.markdown("### 📋 Your Mood Report")
                    st.write(report)
            except Exception as e:
                st.warning(f"Demo mode: {str(e)[:100]}")
    

    
    st.markdown("---")
    st.markdown("""
    ### Features
    - Store text, voice, and image memories
    - AI-powered semantic search
    - Chat with AI based on your memories
    - Browse memories by calendar date
    """)

# TEXT MEMORY PAGE
elif st.session_state.page == "text_memory":
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        if st.button("← Back to Home", key="back_text"):
            st.session_state.page = "home"
            st.rerun()
    
    with col3:
        if st.button("Logout", use_container_width=True, key="logout_text"):
            logout()
    
    st.markdown("# 📝 Add Text Memory")
    st.markdown("---")
    
    text = st.text_area("Write your memory", height=150, placeholder="What do you want to remember?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Save Memory", use_container_width=True):
            if text:
                try:
                    with st.spinner("Saving..."):
                        response = requests.post(
                            f"{API}/add_text_memory",
                            data={"text": text, "email": st.session_state.user_email}
                        )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success("✅ Memory saved successfully!")
                        st.balloons()
                    else:
                        st.error(f"Error: {response.status_code}")
                except Exception as e:
                    st.error(f"Connection error: {str(e)}")
            else:
                st.warning("Please write something first")
    
    with col2:
        if st.button("Clear", use_container_width=True):
            st.rerun()

# IMAGE MEMORY PAGE
elif st.session_state.page == "image_memory":
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        if st.button("← Back to Home", key="back_image"):
            st.session_state.page = "home"
            st.rerun()
    
    with col3:
        if st.button("Logout", use_container_width=True, key="logout_image"):
            logout()
    
    st.markdown("# 🖼️ Add Image Memory")
    st.markdown("---")
    
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Image Preview")
            st.image(uploaded_file, use_column_width=True)
        
        with col2:
            st.markdown("### Description")
            
            if st.button("Analyze Image", use_container_width=True):
                try:
                    with st.spinner("Analyzing..."):
                        response = requests.post(
                            f"{API}/add_image_memory",
                            files={"file": uploaded_file}
                        )
                    
                    if response.status_code == 200:
                        description = response.json().get("description")
                        st.session_state.image_desc = description
                        st.success("✅ Image analyzed!")
                        st.info(f"**AI Description:** {description}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            
            if "image_desc" in st.session_state:
                notes = st.text_area("Add notes", placeholder="Any additional notes?", height=100)
                
                if st.button("Save", use_container_width=True):
                    final_text = f"{st.session_state.image_desc}\n\nNotes: {notes}" if notes else st.session_state.image_desc
                    try:
                        requests.post(f"{API}/add_text_memory", data={"text": final_text, "email": st.session_state.user_email})
                        st.success("✅ Saved!")
                        st.balloons()
                        del st.session_state.image_desc
                    except:
                        st.error("Save failed")
    else:
        st.info("Upload an image to start")

# VOICE MEMORY PAGE
elif st.session_state.page == "voice_memory":
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        if st.button("← Back to Home", key="back_voice"):
            st.session_state.page = "home"
            st.rerun()
    
    with col3:
        if st.button("Logout", use_container_width=True, key="logout_voice"):
            logout()
    
    st.markdown("# 🎤 Add Voice Note")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Record Audio")
        audio_bytes = st.audio_input("Click to record")
        
        if audio_bytes:
            st.audio(audio_bytes, format="audio/wav")
    
    with col2:
        st.markdown("### Transcription")
        
        if audio_bytes:
            if st.button("Transcribe", use_container_width=True):
                try:
                    with st.spinner("Converting..."):
                        response = requests.post(
                            f"{API}/add_voice_memory",
                            files={"file": ("audio.wav", audio_bytes, "audio/wav")}
                        )
                    
                    if response.status_code == 200:
                        transcript = response.json().get("transcription")
                        st.session_state.transcript = transcript
                        st.success("✅ Done!")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    st.markdown("---")
    
    if "transcript" in st.session_state:
        st.markdown("### Text from Audio")
        
        edited = st.text_area("Edit if needed", value=st.session_state.transcript, height=120)
        
        if st.button("Save Voice Memory", use_container_width=True):
            try:
                requests.post(f"{API}/add_text_memory", data={"text": edited, "email": st.session_state.user_email})
                st.success("✅ Voice memory saved!")
                st.balloons()
                del st.session_state.transcript
            except:
                st.error("Save failed")

# SEARCH PAGE
elif st.session_state.page == "search":
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        if st.button("← Back to Home", key="back_search"):
            st.session_state.page = "home"
            st.rerun()
    
    with col3:
        if st.button("Logout", use_container_width=True, key="logout_search"):
            logout()
    
    st.markdown("# 🔍 Search Memories")
    st.markdown("---")
    
    query = st.text_input("Ask your life", placeholder="e.g., When did I meet Rahul?")
    
    if st.button("Search", use_container_width=True):
        if query:
            try:
                with st.spinner("Searching..."):
                    response = requests.get(
                        f"{API}/search",
                        params={"query": query}
                    )
                
                if response.status_code == 200:
                    results = response.json().get("results", [])
                    
                    if results:
                        st.success(f"Found {len(results)} memories:")
                        for i, result in enumerate(results, 1):
                            with st.expander(f"Memory {i}"):
                                st.write(result)
                    else:
                        st.info("No results found")
            except Exception as e:
                st.error(f"Error: {str(e)}")

# CALENDAR PAGE
elif st.session_state.page == "calendar":
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        if st.button("← Back to Home", key="back_calendar"):
            st.session_state.page = "home"
            st.rerun()
    
    with col3:
        if st.button("Logout", use_container_width=True, key="logout_calendar"):
            logout()
    
    st.markdown("# 📅 Calendar View")
    st.markdown("---")
    
    selected_date = st.date_input("Select a date", value=date.today())
    
    if st.button("Show Memories", use_container_width=True):
        try:
            with st.spinner("Loading..."):
                response = requests.get(
                    f"{API}/memories_by_date",
                    params={"date": selected_date.strftime("%Y-%m-%d")}
                )
            
            if response.status_code == 200:
                memories = response.json().get("memories", [])
                
                if memories:
                    st.success(f"Found {len(memories)} memories:")
                    for i, memory in enumerate(memories, 1):
                        with st.expander(f"Memory {i}"):
                            st.write(memory.get("content"))
                            st.caption(f"Time: {memory.get('timestamp')}")
                else:
                    st.info("No memories for this date")
        except Exception as e:
            st.error(f"Error: {str(e)}")

    # allow user to write feelings/emotions for this date
    st.markdown("### 💭 How are you feeling on this date?")
    feeling_text = st.text_area("Write something about your emotions or mood:", key="feelings_text")
    if st.button("Save Feelings", use_container_width=True):
        if feeling_text.strip():
            try:
                resp = requests.post(f"{API}/add_text_memory", data={
                    "text": feeling_text,
                    "email": st.session_state.user_email,
                    "date": selected_date.strftime("%Y-%m-%d")
                })
                if resp.status_code == 200:
                    st.success("Feelings saved!")
                    feeling_text = ""
                else:
                    st.error("Failed to save feelings")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please write something before saving.")
    
    st.markdown("---")
    try:
        response = requests.get(f"{API}/memory_stats")
        if response.status_code == 200:
            stats = response.json()
            col1, col2 = st.columns(2)
            col1.metric("Total Memories", stats.get("total_memories", 0))
            col2.metric("Days with Memories", stats.get("days_with_memories", 0))
    except:
        pass

# Initialize chat input state
if "chat_input_key" not in st.session_state:
    st.session_state.chat_input_key = 0

# CHATBOT PAGE
elif st.session_state.page == "chatbot":
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        if st.button("← Back to Home", key="back_chat"):
            st.session_state.page = "home"
            st.rerun()
    
    with col3:
        if st.button("Logout", use_container_width=True, key="logout_chat"):
            logout()
    
    st.markdown("# 💬 Chat with AI")
    st.markdown("---")
    st.info("AI learns from your memories to chat naturally with you")
    
    st.markdown("### Conversation")
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        if st.session_state.chat_history:
            for msg in st.session_state.chat_history:
                with st.chat_message(msg.get("role", "user")):
                    st.write(msg.get("content", ""))
        else:
            st.info("Start a conversation... 💭")
    
    st.markdown("---")
    
    # Input area with proper state management
    col_input, col_send = st.columns([4, 1])
    
    with col_input:
        user_input = st.text_input(
            "Your message:",
            placeholder="Type something...",
            key=f"chat_input_{st.session_state.chat_input_key}",
            label_visibility="collapsed"
        )
    
    with col_send:
        send_clicked = st.button("Send ➤", use_container_width=True, key="btn_send_chat")
    
    # Process message only on send button click
    if send_clicked and user_input:
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Increment input key to clear the text field
        st.session_state.chat_input_key += 1
        
        # Get AI response
        try:
            with st.spinner("AI is thinking..."):
                # Send only last 3 messages for context (not full history to prevent loops)
                recent_history = st.session_state.chat_history[-3:] if len(st.session_state.chat_history) > 1 else []
                
                response = requests.post(
                    f"{API}/chat",
                    json={
                        "message": user_input,
                        "history": recent_history[:-1]  # Exclude current message
                    },
                    timeout=10
                )
            
            if response.status_code == 200:
                ai_message = response.json().get("response", "I understand how you feel.")
                st.session_state.chat_history.append({"role": "assistant", "content": ai_message})
            else:
                st.warning("Demo mode - simple response")
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": "I'm here to listen. Tell me more!"
                })
        except Exception as e:
            st.warning(f"Using offline mode")
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": "That sounds important. I'm listening."
            })
        
        st.rerun()
    
    st.markdown("---")
    
    # Analysis and clear buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💭 Analyze Feelings", use_container_width=True, key="btn_analyze_chat"):
            try:
                with st.spinner("Analyzing your emotions..."):
                    response = requests.get(f"{API}/analyze_feelings")
                
                if response.status_code == 200:
                    analysis = response.json().get("analysis", {})
                    st.markdown("### 📊 Feelings Analysis")
                    
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.markdown(f"**Emotional State:** {analysis.get('emotional_state', 'N/A')}")
                        st.markdown(f"**Themes:** {', '.join(analysis.get('themes', []))}")
                    
                    with col_b:
                        emotions = analysis.get('emotions', [])
                        st.markdown(f"**Emotions Detected:**")
                        for emotion in emotions:
                            st.write(f"• {emotion}")
                    
                    st.success(f"💡 {analysis.get('insight', 'Keep sharing your feelings')}")
                else:
                    st.warning("Could not analyze - running in demo mode")
            except Exception as e:
                st.warning(f"Demo mode: {str(e)[:100]}")
    
    with col2:
        if st.button("📈 Mood Report", use_container_width=True, key="btn_report_chat"):
            try:
                with st.spinner("Generating mood report..."):
                    response = requests.get(f"{API}/mood_report")
                
                if response.status_code == 200:
                    report = response.json().get("report", "")
                    st.markdown("### 📋 Your Mood Report")
                    st.write(report)
            except Exception as e:
                st.warning(f"Demo mode: {str(e)[:100]}")
    
    with col3:
        if st.button("Clear Chat", use_container_width=True, key="btn_clear_chat"):
            st.session_state.chat_history = []
            st.session_state.chat_input_key += 1
            st.rerun()
