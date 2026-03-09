# Read the original clean part up to calendar
with open(r'frontend\app.py', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

# Keep only up to the end of calendar page
clean_lines = []
for i, line in enumerate(lines):
    clean_lines.append(line)
    if 'stats = r.json()' in line and i > 300:
        # Found end of calendar section, keep a few more lines
        for j in range(i+1, min(i+15, len(lines))):
            if 'elif st.session_state.page ==' in lines[j]:
                break
            clean_lines.append(lines[j])
        break

# Add mood analysis and chatbot pages
mood_and_chat_code = '''
# MOOD ANALYSIS PAGE
elif st.session_state.page == "mood_analysis":
    if st.button("← Back to Home"):
        st.session_state.page = "home"
        st.rerun()
    
    st.markdown("# 💭 Your Mood Analysis")
    st.markdown("---")
    
    st.info("🤖 Analyzing your emotions based on your saved memories...")
    
    if st.button("Analyze My Feelings", use_container_width=True):
        try:
            with st.spinner("Analyzing memories..."):
                r = requests.get(f"{API}/analyze_mood")
            
            if r.status_code == 200:
                data = r.json()
                mood = data.get("mood", "neutral")
                sentiment = data.get("sentiment", "")
                analysis = data.get("analysis", "")
                keywords = data.get("keywords", [])
                
                st.session_state.user_mood = mood
                
                # Display mood
                mood_emoji = {
                    "happy": "😊",
                    "sad": "😔",
                    "anxious": "😰",
                    "excited": "🤗",
                    "calm": "😌",
                    "neutral": "😐"
                }
                
                st.success(f"Your Current Mood: {mood_emoji.get(mood, '😐')} **{mood.upper()}**")
                st.write(f"**Sentiment:** {sentiment}%")
                st.info(analysis)
                
                if keywords:
                    st.markdown("### 📌 Key Themes")
                    for kw in keywords:
                        st.write(f"● {kw}")
            else:
                st.error("Error analyzing mood")
        except Exception as e:
            st.error(f"Connection error: {e}")

# CHATBOT PAGE
elif st.session_state.page == "chatbot":
    if st.button("← Back to Home"):
        st.session_state.page = "home"
        st.rerun()
    
    st.markdown("# 🤖 Chat with AI")
    st.markdown("---")
    
    if not st.session_state.user_mood:
        if st.button("Load Your Mood First", use_container_width=True):
            st.session_state.page = "mood_analysis"
            st.rerun()
        st.info("First analyze your mood to get personalized chat")
    else:
        st.success(f"💭 Chat based on your mood: **{st.session_state.user_mood.upper()}**")
        
        # Display chat history
        st.markdown("### 💬 Conversation")
        chat_container = st.container()
        
        with chat_container:
            for msg in st.session_state.chat_messages:
                if msg["role"] == "user":
                    st.markdown(f"**You:** {msg['content']}")
                else:
                    st.markdown(f"**AI:** {msg['content']}")
        
        st.markdown("---")
        
        # Input for user message
        user_input = st.text_input("Your message:", placeholder="Talk to me...")
        
        if st.button("Send", use_container_width=True):
            if user_input:
                st.session_state.chat_messages.append({"role": "user", "content": user_input})
                
                try:
                    with st.spinner("Thinking..."):
                        r = requests.post(
                            f"{API}/chat",
                            json={
                                "message": user_input,
                                "mood": st.session_state.user_mood,
                                "history": st.session_state.chat_messages
                            }
                        )
                    
                    if r.status_code == 200:
                        ai_response = r.json().get("response", "I understand how you feel...")
                        st.session_state.chat_messages.append({"role": "ai", "content": ai_response})
                        st.rerun()
                    else:
                        st.error("Error getting response")
                except Exception as e:
                    st.error(f"Connection error: {e}")
        
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.chat_messages = []
            st.rerun()
'''

# Write the fixed file
with open(r'frontend\app.py', 'w', encoding='utf-8') as f:
    f.writelines(clean_lines)
    f.write(mood_and_chat_code)

print("File fixed successfully!")
