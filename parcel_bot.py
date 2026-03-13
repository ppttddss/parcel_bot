import streamlit as st
import requests
import json
import os

st.set_page_config(page_title="Insurance Grok", page_icon="🔵", layout="wide")

# ─── Minimal clean CSS ───
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;500;600&display=swap');

    body, .stApp {
        background: #ffffff !important;
        color: #111111 !important;
        font-family: 'Segoe UI', sans-serif !important;
    }
    .main .block-container {
        max-width: 900px !important;
        padding: 2rem 1.5rem 4rem !important;
    }
    .chat-area {
        border: 1px solid #d0d0d0 !important;
        border-radius: 10px !important;
        background: white !important;
        overflow: hidden;
    }
    h1 {
        font-size: 2.1rem !important;
        font-weight: 600 !important;
        color: #005a9e !important;
        text-align: center !important;
        margin: 0 0 0.6rem 0 !important;
    }
    .subtitle {
        color: #555 !important;
        text-align: center !important;
        font-size: 0.95rem !important;
        margin-bottom: 1.5rem !important;
    }
    .stChatMessage {
        border-radius: 14px !important;
        padding: 12px 16px !important;
        margin: 0.9rem 0 !important;
        max-width: 78% !important;
    }
    .user .stChatMessage {
        background: #005a9e !important;
        color: white !important;
        margin-left: auto !important;
    }
    .assistant .stChatMessage {
        background: #f8f9fa !important;
        color: #111 !important;
        border: 1px solid #e5e5e5 !important;
    }
    .stChatInput > div > div {
        background: #ffffff !important;
        border: 1px solid #c0c0c0 !important;
        border-radius: 999px !important;
        padding: 0.3rem 0.9rem !important;
    }
    .stChatInput input {
        color: #111 !important;
    }
    .stChatInput button {
        background: #005a9e !important;
        color: white !important;
        border-radius: 50% !important;
        width: 40px !important;
        height: 40px !important;
        margin-left: 6px !important;
    }
    .placeholder {
        text-align: center;
        color: #777;
        padding: 5rem 1rem;
        font-size: 1.1rem;
    }
    .footer {
        color: #666;
        font-size: 0.8rem;
        text-align: center;
        margin-top: 2.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# ─── Title ───
st.markdown("<h1>Insurance Grok</h1>", unsafe_allow_html=True)
st.markdown('<div class="subtitle">Shared memory • Powered by xAI</div>', unsafe_allow_html=True)

# ─── API Key check ───
api_key = st.secrets.get("XAI_API_KEY")
if not api_key:
    st.error("API key missing. Add XAI_API_KEY in Streamlit → Secrets.")
    st.stop()

# ─── Memory ───
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
        {"role": "assistant", "content": "Hello — Insurance Grok here. Memory active. How can I assist?"}
    ]
    save_memory(st.session_state.messages)

if "current_session" not in st.session_state:
    st.session_state.current_session = []

# ─── Sidebar (very minimal) ───
with st.sidebar:
    st.markdown("**Options**")
    show_recent = st.checkbox("Show last 20 messages", value=False)

# ─── Chat content ───
with st.container():
    messages_to_show = []
    if show_recent:
        messages_to_show = st.session_state.messages[-20:]
    messages_to_show += st.session_state.current_session

    for msg in messages_to_show:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if not messages_to_show:
        st.markdown("""
            <div class="placeholder">
                Ready when you are<br>
                <span style="font-size:0.95rem;">Memory is active. Ask anything.</span>
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
        with st.spinner("…"):
            recent_context = st.session_state.messages[-20:]

            try:
                r = requests.post(
                    "https://api.x.ai/v1/chat/completions",
                    headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
                    json={
                        "model": "grok-4.20-beta-0309-non-reasoning",
                        "messages": [
                            {"role": "system", "content": "You are Insurance Grok by xAI. Focus on insurance topics: policies, claims, coverage, underwriting, risk. Be precise, professional, clear. Use full memory context."}
                        ] + recent_context
                    },
                    timeout=80
                )
                r.raise_for_status()
                answer = r.json()["choices"][0]["message"]["content"]

                assistant_msg = {"role": "assistant", "content": answer}
                st.session_state.messages.append(assistant_msg)
                st.session_state.current_session.append(assistant_msg)
                st.markdown(answer)

            except Exception as e:
                err_text = f"Error: {str(e)}"
                st.error(err_text)
                err_msg = {"role": "assistant", "content": err_text}
                st.session_state.messages.append(err_msg)
                st.session_state.current_session.append(err_msg)

    save_memory(st.session_state.messages)

# ─── Footer ───
st.markdown('<div class="footer">Powered by xAI • Insurance Grok • Memory active (hidden by default)</div>', unsafe_allow_html=True)
