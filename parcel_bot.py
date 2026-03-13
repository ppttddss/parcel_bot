import streamlit as st
import requests
import json
import os

st.set_page_config(page_title="Insurance Grok • Team", page_icon="🟦", layout="wide")

# ─── Custom CSS: Clean grok.com-inspired but sharp blue, white bg, no gradients ───
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;500;600;700&display=swap');

    body, .stApp {
        background: #ffffff !important;
        font-family: 'Segoe UI', system-ui, sans-serif !important;
        color: #111111 !important;
    }
    .main .block-container {
        max-width: 960px !important;
        padding: 1.5rem 1rem 5rem !important;
    }
    .chat-container {
        background: white !important;
        border: 1px solid #0067c5 !important;
        border-radius: 12px !important;
        overflow: hidden;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06) !important;
    }
    .header {
        padding: 1.4rem 2rem !important;
        text-align: center !important;
        border-bottom: 1px solid #e0e0e0 !important;
        background: white !important;
    }
    .header h1 {
        margin: 0 !important;
        font-size: 2.2rem !important;
        font-weight: 600 !important;
        color: #0067c5 !important;
        display: inline-flex !important;
        align-items: center !important;
        gap: 0.6rem !important;
    }
    .header .logo {
        font-size: 2.4rem !important;
        line-height: 1 !important;
    }
    .stChatMessage {
        border-radius: 16px !important;
        padding: 14px 18px !important;
        margin: 1.1rem 0 !important;
        max-width: 80% !important;
        box-shadow: 0 1px 6px rgba(0,0,0,0.08) !important;
    }
    .user .stChatMessage {
        background: #0067c5 !important;
        color: white !important;
        margin-left: auto !important;
    }
    .assistant .stChatMessage {
        background: #f5f5f5 !important;
        color: #111111 !important;
        border: 1px solid #e0e0e0 !important;
    }
    .stChatInput > div > div {
        background: white !important;
        border: 1px solid #0067c5 !important;
        border-radius: 999px !important;
        padding: 0.4rem 1rem !important;
    }
    .stChatInput input {
        color: #111111 !important;
    }
    .stChatInput button {
        background: #0067c5 !important;
        color: white !important;
        border-radius: 50% !important;
        width: 44px !important;
        height: 44px !important;
        margin-left: 8px !important;
    }
    .sidebar-toggle {
        background: #0067c5 !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.4rem 0.9rem !important;
    }
    .caption {
        color: #555 !important;
        font-size: 0.82rem !important;
        text-align: center !important;
        margin-top: 2.5rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# ─── Header: simple blue grok logo + title in blue ───
st.markdown("""
    <div class="header">
        <h1>
            <span class="logo">🟦</span> Insurance Grok Team
        </h1>
        <p style="margin: 0.3rem 0 0; color: #555; font-size: 1rem;">
            Shared memory • Powered by xAI
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
        {"role": "assistant", "content": "Hello team — Insurance Grok here. Full memory active. How can I help with insurance today?"}
    ]
    save_memory(st.session_state.messages)

if "current_session" not in st.session_state:
    st.session_state.current_session = []

# ─── Minimal sidebar for history toggle ───
with st.sidebar:
    st.markdown("<h4 style='color:#0067c5; margin-bottom:1rem;'>Options</h4>", unsafe_allow_html=True)
    view_history = st.checkbox("View last 20 team messages", value=False,
                               help="Show recent shared history. Leave unchecked for clean view.")

# ─── Chat display ───
chat_container = st.container()
with chat_container:
    display_messages = []
    if view_history:
        display_messages = st.session_state.messages[-20:]
    display_messages += st.session_state.current_session

    for msg in display_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if not display_messages:
        st.markdown("""
            <div style="text-align:center; color:#777; padding:6rem 1rem;">
                <h3 style="color:#333; margin-bottom:0.8rem;">Ready when you are</h3>
                <p style="font-size:1.05rem;">Team memory is active. Ask anything.</p>
            </div>
        """, unsafe_allow_html=True)

# ─── Input ───
if prompt := st.chat_input("Ask Insurance Grok anything…"):
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
                            {"role": "system", "content": "You are Insurance Grok by xAI. You help with insurance questions, claims, policies, coverage, and risk. Use full team memory context. Be clear, accurate, helpful and professional."}
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
    <div class="caption">
        Powered by xAI • Insurance Grok • Team memory active (hidden by default)
    </div>
""", unsafe_allow_html=True)
