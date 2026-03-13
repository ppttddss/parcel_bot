import streamlit as st
import requests
import json
import os

st.set_page_config(page_title="Insurance Grok", layout="wide")

# Main dark black & white styling + fly-out settings
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
        font-size: 2.6rem !important;
        margin: 1.5rem 0 2.2rem 0 !important;
        font-weight: 400 !important;
    }
    /* Messages */
    .stChatMessage {
        background: #000000 !important;
        color: #ffffff !important;
        border: none !important;
        padding: 1.4rem 0 !important;
        margin: 2rem 0 !important;
        line-height: 1.65 !important;
        font-size: 1.25rem !important;
    }
    .user .stChatMessage { text-align: right !important; }
    .assistant .stChatMessage { text-align: left !important; }

    /* Input - shorter, pure black */
    .stChatInput,
    .stChatInput > div,
    .stChatInput > div > div,
    .stChatInput input {
        background: #000000 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        padding: 0.6rem 0 !important;
        font-size: 1.25rem !important;
        line-height: 1.3 !important;
    }
    .stChatInput input::placeholder {
        color: #ffffff !important;
        opacity: 0.6 !important;
    }
    .stChatInput button,
    .stChatInput button > div,
    .stChatInput button svg {
        background: #000000 !important;
        color: #ffffff !important;
        fill: #ffffff !important;
        border: none !important;
        border-radius: 0 !important;
        padding: 0.6rem !important;
        margin-left: 1.2rem !important;
    }
    .stChatInput button:hover {
        background: #111111 !important;
    }

    /* Fly-out settings panel */
    .settings-flyout {
        position: fixed !important;
        top: 1rem !important;
        right: 1.5rem !important;
        z-index: 999 !important;
        background: #111111 !important;
        border: 1px solid #222222 !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        width: 280px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.6) !important;
        color: #ffffff !important;
    }
    .settings-flyout [data-testid="stExpander"] {
        background: transparent !important;
        border: none !important;
    }
    .settings-flyout summary {
        color: #ffffff !important;
        font-size: 1rem !important;
        cursor: pointer !important;
    }
    .settings-flyout .stCheckbox {
        color: #ffffff !important;
    }

    /* Hide unwanted elements */
    footer, header, section[data-testid="stSidebar"], .stDeployButton {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown("<h1>Insurance Grok</h1>", unsafe_allow_html=True)

# Fly-out settings panel (top-right)
with st.expander("Settings", expanded=False):
    st.markdown('<div class="settings-flyout">', unsafe_allow_html=True)
    show_hist = st.checkbox("Show last 20 messages", value=False)
    st.markdown('</div>', unsafe_allow_html=True)

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

    save(st.session_state.messages)
