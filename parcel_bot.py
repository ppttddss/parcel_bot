import streamlit as st
import requests
import json
import os

st.set_page_config(page_title="Insurance Grok", layout="wide")

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
        padding: 2rem 1.5rem 4rem !important;
        background: #000000 !important;
    }
    h1 {
        color: #ffffff !important;
        text-align: center !important;
        font-size: 2.5rem !important;
        margin: 1.8rem 0 2.5rem 0 !important;
        font-weight: 400 !important;
    }
    /* Messages - more flow / spacing */
    .stChatMessage {
        background: #000000 !important;
        color: #ffffff !important;
        border: none !important;
        padding: 1.2rem 0 !important;
        margin: 1.8rem 0 !important;
        line-height: 1.6 !important;
        font-size: 1.05rem !important;
    }
    .user .stChatMessage {
        text-align: right !important;
    }
    .assistant .stChatMessage {
        text-align: left !important;
    }
    /* Input area - FORCE ALL BLACK, no grey anywhere */
    .stChatInput,
    .stChatInput > div,
    .stChatInput > div > div,
    .stChatInput > div > div > div,
    .stChatInput textarea,
    .stChatInput input {
        background: #000000 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        padding: 1rem 0 !important;
        font-size: 1.1rem !important;
    }
    .stChatInput input::placeholder,
    .stChatInput textarea::placeholder {
        color: #ffffff !important;
        opacity: 0.55 !important;
    }
    .stChatInput button,
    .stChatInput button > div,
    .stChatInput button svg {
        background: #000000 !important;
        color: #ffffff !important;
        fill: #ffffff !important;
        border: none !important;
        border-radius: 0 !important;
        padding: 1rem !important;
        margin-left: 1.2rem !important;
    }
    .stChatInput button:hover {
        background: #111111 !important;
    }
    /* Hide everything unnecessary */
    footer, header, section[data-testid="stSidebar"], .stDeployButton, .st-emotion-cache-1y4p8pa {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>Insurance Grok</h1>", unsafe_allow_html=True)

api_key = st.secrets.get("XAI_API_KEY")
if not api_key:
    st.error("Missing API key.")
    st.stop()

MEMORY_FILE = "memory.json"

def load():
    if os.path.exists(MEMORY_FILE):
        try: return json.load(open(MEMORY_FILE, "r", encoding="utf-8"))
        except: return []
    return []

def save(msgs):
    json.dump(msgs, open(MEMORY_FILE, "w", encoding="utf-8"), indent=None)

if "messages" not in st.session_state:
    st.session_state.messages = load()
    if not st.session_state.messages:
        st.session_state.messages = [{"role": "assistant", "content": "Ready."}]
        save(st.session_state.messages)

for msg in st.session_state.messages:
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

    save(st.session_state.messages)
