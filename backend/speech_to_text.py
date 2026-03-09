def transcribe_audio(file_path):
    """
    Transcribe audio file to text using OpenAI Whisper.
    For demo purposes, returns a placeholder if Whisper is not available.
    """
    try:
        import openai_whisper as whisper
        model = whisper.load_model("base")
        result = model.transcribe(file_path)
        return result["text"]
    except Exception as e:
        # Demo mode: Return intelligent placeholder based on file size
        # Larger files = more content "transcribed"
        import os
        file_size = os.path.getsize(file_path)
        
        # Simulate transcription based on file size
        demo_messages = {
            "short": "[Demo Mode] This is a short voice note. Please provide your own transcription or use a real API key.",
            "medium": "[Demo Mode] This appears to be a longer voice message with multiple thoughts. Feel free to edit and add your actual message content.",
            "long": "[Demo Mode] This is an extended voice message. The system is ready to transcribe real audio when Whisper is properly configured."
        }
        
        if file_size < 10000:
            return demo_messages["short"]
        elif file_size < 50000:
            return demo_messages["medium"]
        else:
            return demo_messages["long"]
