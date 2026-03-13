import streamlit as st
import requests
import json
import os

st.set_page_config(page_title="Insurance Grok", layout="wide")

# Force dark theme - black background, white text
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;500;600&display=swap');

    html, body, [data-testid="stAppViewContainer"], .stApp {
        background: #000000 !important;
        color: #ffffff !important;
        font-family: 'Segoe UI', sans-serif !important;
    }
    .main .block-container {
        max-width: 900px !important;
        padding: 1.5rem 1rem 4rem !important;
        background: #000000 !important;
    }
    h1 {
        color: #ffffff !important;
        text-align: center !important;
        font-size: 2.2rem !important;
        margin-bottom: 0.6rem !important;
    }
    .subtitle {
        color: #cccccc !important;
        text-align: center !important;
        font-size: 0.95rem !important;
        margin-bottom: 1.8rem !important;
    }
    .stChatMessage {
        border-radius: 14px !important;
        padding: 12px 16px !important;
        margin: 0.9rem 0 !important;
        max-width: 78% !important;
        border: 1px solid #333333 !important;
    }
    .user .stChatMessage {
        background: #1a3c6e !important;
        color: #ffffff !important;
        margin-left: auto !important;
    }
    .assistant .stChatMessage {
        background: #1e1e1e !important;
        color: #e0e0e0 !important;
    }
    .stChatInput > div > div {
        background: #111111 !important;
        border: 1px solid #444444 !important;
        border-radius: 999px !important;
        padding: 0.4rem 1rem !important;
        color: #ffffff !important;
    }
    .stChatInput input {
        color: #ffffff !important;
        background: transparent !important;
    }
    .stChatInput button {
        background: #1a3c6e !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 50% !important;
        width: 42px !important;
        height: 42px !important;
        margin-left: 8px !important;
    }
    .placeholder {
        text-align: center;
        color: #aaaaaa;
        padding: 6rem 1rem;
        font-size: 1.1rem;
    }
    .footer {
        color: #888888 !important;
        font-size: 0.8rem !important;
        text-align: center !important;
        margin-top: 3rem !important;
    }
    footer { visibility: hidden !important; }
    header, section[data-testid="stSidebar"] { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown("<h1>Insurance Grok</h1>", unsafe_allow_html=True)
st.markdown('<div class="subtitle">Shared memory • Powered by xAI</div>', unsafe_allow_html=True)

# API Key
api_key = st.secrets.get("XAI_API_KEY")
if not api_key:
    st.error("Missing API key — set XAI_API_KEY in secrets.")
    st.stop()

# Memory handling
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
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello — Insurance Grok here. Ready to help."}
    ]
    save_memory(st.session_state.messages)

if "current_session" not in st.session_state:
    st.session_state.current_session = []

# Sidebar toggle (hidden if you prefer — can remove this block)
with st.sidebar:
    st.checkbox("Show recent 20 messages", key="show_hist", value=False)

# Display messages
display_msgs = st.session_state.messages[-20:] if st.session_state.get("show_hist", False) else []
display_msgs += st.session_state.current_session

for msg in display_msgs:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if not display_msgs:
    st.markdown("""
        <div class="placeholder">
            Ready when you are<br>
            <span style="font-size:0.95rem;">Memory is active. Ask anything.</span>
        </div>
    """, unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("Ask Insurance Grok…"):
    user_msg = {"role": "user", "content": prompt}
    st.session_state.messages.append(user_msg)
    st.session_state.current_session.append(user_msg)

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("…"):
            recent = st.session_state.messages[-20:]

            try:
                response = requests.post(
                    "https://api.x.ai/v1/chat/completions",
                    headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
                    json={
                        "model": "grok-4.20-beta-0309-non-reasoning",
                        "messages": [
                            {"role": "system", "content": "You are Insurance Grok. Insurance expert. Precise, professional."}
                        ] + recent
                    },
                    timeout=75
                ).json()
                reply = response["choices"][0]["message"]["content"]

                assistant_msg = {"role": "assistant", "content": reply}
                st.session_state.messages.append(assistant_msg)
                st.session_state.current_session.append(assistant_msg)
                st.markdown(reply)

            except Exception as e:
                err = f"Error: {str(e)}"
                st.error(err)
                st.session_state.messages.append({"role": "assistant", "content": err})

    save_memory(st.session_state.messages)

st.markdown('<div class="footer">Powered by xAI • Insurance Grok • Memory active</div>', unsafe_allow_html=True)
