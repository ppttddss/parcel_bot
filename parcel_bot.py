import streamlit as st
import requests
import json
import os

st.set_page_config(page_title="Insurance Grok", layout="wide")

# Very light, minimal CSS — no dark colors at all
st.markdown("""
    <style>
    body, .stApp { background: white !important; color: #111 !important; }
    .main .block-container { max-width: 880px; padding: 1.8rem 1.2rem 4rem; }
    h1 { color: #004b8d; text-align: center; font-size: 2.2rem; margin-bottom: 0.4rem; }
    .subtitle { color: #555; text-align: center; font-size: 0.95rem; margin-bottom: 1.8rem; }
    .stChatMessage { border-radius: 12px; padding: 12px 16px; margin: 0.8rem 0; max-width: 75%; }
    .user .stChatMessage { background: #004b8d !important; color: white !important; margin-left: auto; }
    .assistant .stChatMessage { background: #f9f9f9; border: 1px solid #e0e0e0; }
    .stChatInput > div > div { border: 1px solid #c0c0c0 !important; border-radius: 999px; background: white !important; }
    .stChatInput input { color: #111 !important; }
    .stChatInput button { background: #004b8d !important; }
    .placeholder { text-align: center; color: #666; padding: 6rem 1rem; }
    .footer { color: #777; font-size: 0.8rem; text-align: center; margin-top: 3rem; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>Insurance Grok</h1>", unsafe_allow_html=True)
st.markdown('<div class="subtitle">Shared memory • Powered by xAI</div>', unsafe_allow_html=True)

api_key = st.secrets.get("XAI_API_KEY")
if not api_key:
    st.error("Missing API key — set XAI_API_KEY in secrets.")
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
    st.session_state.messages = [{"role": "assistant", "content": "Hello — Insurance Grok here. Ready to help."}]
    save(st.session_state.messages)

if "current" not in st.session_state:
    st.session_state.current = []

with st.sidebar:
    st.checkbox("Show recent 20 msgs", key="show_hist", value=False)

display = st.session_state.messages[-20:] if st.session_state.show_hist else []
display += st.session_state.current

for msg in display:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if not display:
    st.markdown('<div class="placeholder">Ready when you are<br><small>Memory active. Ask anything.</small></div>', unsafe_allow_html=True)

if prompt := st.chat_input("Ask Insurance Grok…"):
    um = {"role": "user", "content": prompt}
    st.session_state.messages.append(um)
    st.session_state.current.append(um)
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("…"):
            try:
                r = requests.post(
                    "https://api.x.ai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                    json={
                        "model": "grok-4.20-beta-0309-non-reasoning",
                        "messages": [{"role": "system", "content": "You are Insurance Grok. Insurance expert. Precise, professional."}] + st.session_state.messages[-20:]
                    },
                    timeout=75
                ).json()
                reply = r["choices"][0]["message"]["content"]
                am = {"role": "assistant", "content": reply}
                st.session_state.messages.append(am)
                st.session_state.current.append(am)
                st.markdown(reply)
            except Exception as e:
                st.error(str(e))
                st.session_state.messages.append({"role": "assistant", "content": f"Error: {str(e)}"})

    save(st.session_state.messages)

st.markdown('<div class="footer">Powered by xAI • Insurance Grok • Memory active</div>', unsafe_allow_html=True)
