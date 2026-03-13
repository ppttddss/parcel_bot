import streamlit as st
import requests
import json
import os

st.set_page_config(page_title="Grok Team • Clean View", page_icon="🟢", layout="wide")

# ─── Custom CSS for SuperGrok-like premium look ───
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    body, .stApp {
        background: linear-gradient(135deg, #0f0f17 0%, #0a0a12 100%);
        color: #e0e0ff;
        font-family: 'Inter', sans-serif;
    }
    .stApp > header { background: transparent !important; }
    section[data-testid="stSidebar"] { display: none !important; }  /* hide sidebar by default */
    .main .block-container {
        max-width: 900px !important;
        padding-top: 2rem !important;
        padding-bottom: 6rem !important;
    }
    .stChatMessage {
        border-radius: 18px !important;
        padding: 14px 18px !important;
        margin-bottom: 1.2rem !important;
        max-width: 80% !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    .user .stChatMessage {
        background: linear-gradient(135deg, #22c55e, #16a34a) !important;
        color: black !important;
        margin-left: auto !important;
    }
    .assistant .stChatMessage {
        background: #1e1e38 !important;
        border: 1px solid #333366;
    }
    .stChatInput > div > div {
        background: #1a1a2e !important;
        border: 1px solid #333366 !important;
        border-radius: 999px !important;
        padding: 0.4rem 1rem !important;
    }
    .stChatInput input {
        color: white !important;
    }
    .stChatInput button {
        background: #22c55e !important;
        color: black !important;
        border-radius: 50% !important;
        width: 48px !important;
        height: 48px !important;
        margin-left: 8px !important;
    }
    h1, h2, h3 { color: #ffffff !important; }
    .stSpinner > div > div { border-top-color: #22c55e !important; }
    footer { visibility: hidden; }
    .caption { color: #8888aa !important; font-size: 0.8rem !important; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# ─── Header ───
st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="font-size: 2.8rem; margin: 0; color: #ffffff;">
            🟢 Grok Team
        </h1>
        <p style="color: #a0a0ff; font-size: 1.1rem; margin-top: 0.3rem;">
            Shared memory • Clean & powerful
        </p>
    </div>
""", unsafe_allow_html=True)

# ─── API KEY FROM SECRETS ───
api_key = st.secrets.get("XAI_API_KEY")
if not api_key:
    st.error("No API key found. Add XAI_API_KEY in Streamlit Settings → Secrets.")
    st.stop()

# ─── TEAM MEMORY ───
MEMORY_FILE = "team_memory.json"

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
        json.dump(messages, f, ensure_ascii=False, indent=2)

if "messages" not in st.session_state:
    st.session_state.messages = load_memory()

if not st.session_state.messages:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hey team — Grok here. Full memory active. Ask anything."}
    ]
    save_memory(st.session_state.messages)

if "current_session" not in st.session_state:
    st.session_state.current_session = []

# ─── Controls (minimal, toggleable via query param or secret button if needed) ───
show_history = False  # default super clean — change to True if you want last 20 always visible

# ─── DISPLAY (only current session by default) ───
display_messages = st.session_state.current_session[:]

if show_history:
    display_messages = st.session_state.messages[-20:] + st.session_state.current_session

for msg in display_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if not display_messages:
    st.markdown("""
        <div style="text-align:center; color:#8888aa; padding:4rem 1rem;">
            <h3 style="color:#cccccc;">Ready when you are</h3>
            <p>Team memory is active in the background — type to begin.</p>
        </div>
    """, unsafe_allow_html=True)

# ─── INPUT ───
if prompt := st.chat_input("Ask anything…"):
    user_msg = {"role": "user", "content": prompt}
    st.session_state.messages.append(user_msg)
    st.session_state.current_session.append(user_msg)

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            recent_for_api = st.session_state.messages[-20:]

            try:
                response = requests.post(
                    "https://api.x.ai/v1/chat/completions",
                    headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
                    json={
                        "model": "grok-4.20-beta-0309-non-reasoning",
                        "messages": [
                            {"role": "system", "content": "You are Grok by xAI. Truthful, helpful, witty. Use full team memory context."}
                        ] + recent_for_api
                    },
                    timeout=90
                )
                response.raise_for_status()
                reply = response.json()["choices"][0]["message"]["content"]

                assistant_msg = {"role": "assistant", "content": reply}
                st.session_state.messages.append(assistant_msg)
                st.session_state.current_session.append(assistant_msg)
                st.markdown(reply)

            except Exception as e:
                error = f"Error: {str(e)}"
                st.error(error)
                err_msg = {"role": "assistant", "content": error}
                st.session_state.messages.append(err_msg)
                st.session_state.current_session.append(err_msg)

    save_memory(st.session_state.messages)

# ─── Footer ───
st.markdown("""
    <div class="caption" style="margin-top: 3rem;">
        Powered by xAI • Grok • Team memory active (hidden view)
    </div>
""", unsafe_allow_html=True)
