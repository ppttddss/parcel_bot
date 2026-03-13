import streamlit as st
import requests
import json
import os

st.set_page_config(page_title="Insurance Grok", layout="wide")

# Pure black & white, no borders on input, larger placeholder
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background: #000000 !important;
        color: #ffffff !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    .main .block-container {
        max-width: 1100px !important;
        padding: 2rem 2.5rem 4rem !important;
        background: #000000 !important;
        margin: 0 auto !important;
    }
    h1 {
        color: #ffffff !important;
        text-align: center !important;
        font-size: 2.8rem !important;
        margin: 1.5rem 0 1.2rem 0 !important;
        font-weight: 400 !important;
    }
    .checkbox-container {
        text-align: center !important;
        margin: 0 0 2rem 0 !important;
        font-size: 1.1rem !important;
    }
    .checkbox-container .stCheckbox {
        display: inline-flex !important;
        align-items: center !important;
    }
    .checkbox-container label {
        color: #ffffff !important;
        font-size: 1.1rem !important;
    }
    .stChatMessage {
        background: #000000 !important;
        color: #ffffff !important;
        border: none !important;
        padding: 1.5rem 0 !important;
        margin: 2.2rem 0 !important;
        line-height: 1.7 !important;
        font-size: 1.3rem !important;
    }
    .user .stChatMessage { text-align: right !important; }
    .assistant .stChatMessage { text-align: left !important; }

    /* Input - no border, dark grey bg, huge white placeholder */
    .stChatInput,
    .stChatInput > div,
    .stChatInput > div > div,
    .stChatInput input {
        background: #111111 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        box-shadow: none !important;
        padding: 0.8rem 1.2rem !important;
        font-size: 1.5rem !important;           /* much larger text */
        line-height: 1.4 !important;
    }
    .stChatInput input::placeholder {
        color: #ffffff !important;
        opacity: 0.8 !important;
        font-size: 1.5rem !important;
    }
    .stChatInput button,
    .stChatInput button > div,
    .stChatInput button svg {
        background: #111111 !important;
        color: #ffffff !important;
        fill: #ffffff !important;
        border: none !important;
        padding: 0.8rem 1.2rem !important;
        margin-left: 1rem !important;
    }
    .stChatInput button:hover {
        background: #222222 !important;
    }

    /* Hide everything else */
    footer, header, section[data-testid="stSidebar"], .stDeployButton {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown("<h1>Insurance Grok</h1>", unsafe_allow_html=True)

# Simple checkbox below title (centered)
show_hist = st.checkbox("Show last 20 messages", value=False, key="show_hist")

api_key = st.secrets.get("XAI_API_KEY")
if not api_key:
    st.error("Missing API key.")
    st.stop()

MEMORY_FILE = "memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_memory(messages):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=None)

if "messages" not in st.session_state:
    st.session_state.messages = load_memory()
    if not st.session_state.messages:
        st.session_state.messages = [{"role": "assistant", "content": "Ready."}]
        save_memory(st.session_state.messages)

# Display messages
display_msgs = st.session_state.messages[-20:] if show_hist else st.session_state.messages
for msg in display_msgs:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask…"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner(""):
            try:
                r = requests.post(
                    "https://api.x.ai/v1/chat/completions",
                    headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
                    json={
                        "model": "grok-4.20-beta-0309-non-reasoning",
                        "messages": st.session_state.messages
                    },
                    timeout=60
                ).json()
                reply = r["choices"][0]["message"]["content"]
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.markdown(reply)
            except Exception as e:
                st.markdown(f"Error: {str(e)}")

    save_memory(st.session_state.messages)
