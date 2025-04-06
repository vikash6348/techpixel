import streamlit as st
import os
import google.generativeai as genai
import json
import requests
from nltk.corpus import wordnet
import streamlit.components.v1 as components

# Streamlit Page Config
st.set_page_config(page_title="Gemini AI Chatbot", page_icon="🌌", layout="wide")
st.title("🌌 WELCOME TO WRITING ASSISTANT CHATBOT!")
st.subheader("I'm your AI-powered writing assistant for grammar correction, content creation, and synonym suggestions.")

# Secure API Key Handling for Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    st.error("Please set the Google API key in environment variables or Streamlit secrets!")
    st.stop()

# Initialize Gemini Client
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro")  # Updated to a valid model

# System Instructions
SYSTEM_PROMPT = """
You are a specialized AI conversational assistant that can perform grammar correction, content creation, and synonym suggestions.

Capabilities:
1. **Grammar Correction**: You can correct grammatical errors in a given text and input must be like this: correct grammar or correct or correct the mistakes in your text and output must be like this: your text with corrections.
2. **Content Creation**: You can generate content based on a given prompt and input must be like this: your content prompt and output must be like this: your content.
3. **Synonym Suggestions**: You can provide synonyms for a given word and input must be like this: suggest synonyms for your word and the output must be like this: synonyms for your word are your word.
4. **Error Handling**: If the user asks for something unrelated to these tasks, inform them that you can only perform these tasks.
"""

# Tool Functions
def correct_grammar(text):
    """Corrects grammatical errors in the provided text using LanguageTool API."""
    url = "https://api.languagetool.org/v2/check"
    payload = {
        'text': text,
        'language': 'en'
    }
    response = requests.post(url, data=payload)
    result = response.json()

    # Extract suggestions from the API response
    corrections = result.get('matches', [])
    for correction in corrections:
        text = text.replace(correction['context']['text'], correction['replacements'][0]['value'])
    return text

def create_content(prompt):
    """Generates content based on the provided prompt using Gemini API."""
    
    # Set your Gemini API key and endpoint
    # Secure API Key Handling
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    st.error("Please set the Google API key in environment variables or Streamlit secrets!")
    st.stop()

# Initialize Gemini AI Client
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro")  # Use a powerful AI model



def suggest_synonyms(word):
    """Suggests synonyms for the provided word using WordNet."""
    synonyms = []
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            if lemma.name() not in synonyms:
                synonyms.append(lemma.name())
    return f"Synonyms for '{word}': {', '.join(synonyms)}"




# Initialize Chat & Task History
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hey there! I am here to turn your ideas into awesome content?"}]
if "task_history" not in st.session_state:
    st.session_state.task_history = []

# Sidebar: Chat and Task History
with st.sidebar:
    st.header("🗂️ Chat & Task History")
    st.write("Click on any task to rerun it.")
    for idx, task in enumerate(reversed(st.session_state.task_history)):
        if st.button(task, key=f"history_{idx}"):
            st.session_state.chat_input = task  # Rerun that task

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle User Input (with rerun from history or typed)
user_input = st.chat_input("Ask me anything...")

# Auto-inject from sidebar history button if needed
if "chat_input" in st.session_state and not user_input:
    user_input = st.session_state.chat_input
    del st.session_state.chat_input

if user_input:
    # Save to histories
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.task_history.append(user_input)

    with st.chat_message("user"):
        st.markdown(user_input)

    # Format messages for Gemini
    messages = [{"role": "assistant", "parts": [SYSTEM_PROMPT]}] + [
        {"role": msg["role"], "parts": [msg["content"]]} for msg in st.session_state.messages
    ]

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = model.generate_content(messages)
            assistant_reply = response.text.strip()

            if assistant_reply.startswith("[CALL:correct_grammar]"):
                try:
                    json_data = assistant_reply[len("[CALL:correct_grammar]"):].strip()
                    params = json.loads(json_data)
                    tool_result = correct_grammar(params.get("text"))
                    assistant_reply = str(tool_result)
                except Exception as e:
                    assistant_reply = f"Error processing grammar correction request: {str(e)}"

            elif assistant_reply.startswith("[CALL:create_content]"):
                try:
                    json_data = assistant_reply[len("[CALL:create_content]"):].strip()
                    params = json.loads(json_data)
                    tool_result = create_content(params.get("prompt"))
                    assistant_reply = str(tool_result)
                except Exception as e:
                    assistant_reply = f"Error processing content creation request: {str(e)}"

            elif assistant_reply.startswith("[CALL:suggest_synonyms]"):
                try:
                    json_data = assistant_reply[len("[CALL:suggest_synonyms]"):].strip()
                    params = json.loads(json_data)
                    tool_result = suggest_synonyms(params.get("word"))
                    assistant_reply = str(tool_result)
                except Exception as e:
                    assistant_reply = f"Error processing synonym suggestion request: {str(e)}"

            st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
            st.markdown(assistant_reply)

# JavaScript for Speech Recognition (Updated)
speech_js = """
    <script>
        if (!('SpeechRecognition' in window || 'webkitSpeechRecognition' in window)) {
            alert('Speech recognition is not supported in this browser.');
        } else {
            var recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = 'en-US';
            recognition.interimResults = true;
            recognition.maxAlternatives = 1;

            recognition.onresult = function(event) {
                var transcript = event.results[0][0].transcript;
                // Set the transcript as the value of the Streamlit input
                window.parent.document.getElementById('speechInput').value = transcript;
            };

            recognition.onerror = function(event) {
                alert('Error occurred: ' + event.error);
            };

            function startRecognition() {
                recognition.start();
            }
        }
    </script>

    <div style="position: fixed; top: 10px; right: 10px; z-index: 9999; background-color: white; padding: 10px; border-radius: 10px; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);">
        <button onclick="startRecognition()" style="font-size: 20px; padding: 10px; background-color: #4CAF50; color: white; border: none; cursor: pointer; border-radius: 5px;">
            🎤 Speak
        </button>
    </div>
"""

# Embed the JavaScript and Speech Input in the right-side corner of Streamlit app
import streamlit.components.v1 as components
components.html(speech_js)
