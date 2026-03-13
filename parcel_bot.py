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

    /* Search/input area - dark grey background + white outline */
    .stChatInput,
    .stChatInput > div,
    .stChatInput > div > div,
    .stChatInput input {
        background: #111111 !important;
        color: #ffffff !important;
        border: 1px solid #ffffff !important;
        border-radius: 8px !important;
        box-shadow: none !important;
        padding: 0.6rem 1rem !important;
        font-size: 1.25rem !important;
        line-height: 1.3 !important;
        transition: border-color 0.2s !important;
    }
    .stChatInput input:focus {
        border-color: #ffffff !important;
        outline: none !important;
    }
    .stChatInput input::placeholder {
        color: #bbbbbb !important;
        opacity: 0.7 !important;
    }
    .stChatInput button,
    .stChatInput button > div,
    .stChatInput button svg {
        background: #111111 !important;
        color: #ffffff !important;
        fill: #ffffff !important;
        border: none !important;
        border-radius: 0 !important;
        padding: 0.6rem !important;
        margin-left: 0.8rem !important;
    }
    .stChatInput button:hover {
        background: #222222 !important;
    }

    /* Modern side fly-out settings */
    .settings-flyout {
        position: fixed !important;
        top: 0 !important;
        right: -320px !important;
        width: 300px !important;
        height: 100% !important;
        background: #111111 !important;
        border-left: 1px solid #333333 !important;
        padding: 2rem 1.5rem !important;
        color: #ffffff !important;
        transition: right 0.3s ease !important;
        z-index: 999 !important;
        overflow-y: auto !important;
    }
    .settings-flyout.open {
        right: 0 !important;
    }
    .flyout-toggle {
        position: fixed !important;
        top: 1rem !important;
        right: 1rem !important;
        background: #111111 !important;
        color: #ffffff !important;
        border: 1px solid #444444 !important;
        border-radius: 6px !important;
        padding: 0.6rem 1rem !important;
        cursor: pointer !important;
        z-index: 1000 !important;
        font-size: 0.95rem !important;
    }
    .flyout-toggle:hover {
        background: #222222 !important;
    }
    .flyout-content h4 {
        margin-top: 0 !important;
        color: #ffffff !important;
    }
    .flyout-content .stCheckbox {
        color: #ffffff !important;
    }

    /* Hide unwanted */
    footer, header, section[data-testid="stSidebar"], .stDeployButton {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown("<h1>Insurance Grok</h1>", unsafe_allow_html=True)

# Fly-out toggle button + hidden checkbox to control open/close
if 'flyout_open' not in st.session_state:
    st.session_state.flyout_open = False

toggle_label = "Close Settings" if st.session_state.flyout_open else "Settings"
if st.button(toggle_label, key="flyout_toggle", help="Open/close settings"):
    st.session_state.flyout_open = not st.session_state.flyout_open
    st.rerun()

# Fly-out panel (slides in from right)
flyout_class = "settings-flyout open" if st.session_state.flyout_open else "settings-flyout"
st.markdown(f'<div class="{flyout_class}">', unsafe_allow_html=True)
st.markdown('<div class="flyout-content">', unsafe_allow_html=True)
st.markdown("<h4>Settings</h4>")
show_hist = st.checkbox("Show last 20 messages", value=False)
st.markdown('</div></div>', unsafe_allow_html=True)

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

# Display
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
