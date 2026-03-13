import streamlit as st
import requests
import json
import os

st.set_page_config(page_title="Insurance Grok", layout="wide")

# Ultra-minimal black & white only
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background: #000000 !important;
        color: #ffffff !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    .main .block-container {
        max-width: 1200px !important;
        padding: 2rem 1rem 2rem !important;
        margin: 0 auto !important;
    }
    h1 {
        color: #ffffff !important;
        text-align: center !important;
        font-size: 2.4rem !important;
        margin: 1.5rem 0 2rem 0 !important;
        font-weight: 500 !important;
    }
    /* Remove all borders, greys, shadows */
    .stChatMessage {
        background: #000000 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 0 !important;
        padding: 1rem 0 !important;
        margin: 1.2rem 0 !important;
        box-shadow: none !important;
    }
    .user .stChatMessage {
        text-align: right !important;
    }
    .assistant .stChatMessage {
        text-align: left !important;
    }
    /* Input - pure black, white text, no grey */
    .stChatInput,
    .stChatInput > div,
    .stChatInput > div > div {
        background: #000000 !important;
        border: none !important;
        border-radius: 0 !important;
        padding: 0.8rem 0 !important;
    }
    .stChatInput input {
        color: #ffffff !important;
        background: #000000 !important;
        caret-color: #ffffff !important;
        border: none !important;
        font-size: 1.1rem !important;
    }
    .stChatInput input::placeholder {
        color: #ffffff !important;
        opacity: 0.6 !important;
    }
    .stChatInput button {
        background: #000000 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 0 !important;
        padding: 0.8rem !important;
        margin-left: 1rem !important;
    }
    .stChatInput button:hover {
        background: #111111 !important;
    }
    /* Hide everything else */
    footer, header, section[data-testid="stSidebar"], .stDeployButton, .reportview-container {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# Just the title — no subtitle
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
    user_msg = {"role": "user", "content": prompt}
    st.session_state.messages.append(user_msg)

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
