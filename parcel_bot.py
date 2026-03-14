import streamlit as st
import requests
import json
import os

st.set_page_config(page_title="Insurance Grok", layout="wide")

st.markdown("""
    
""", unsafe_allow_html=True)

st.markdown("<h1>Insurance Grok</h1>", unsafe_allow_html=True)

show_hist = st.checkbox("Show last 20 messages", value=False)

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

# Key fix: only show messages when checkbox is checked
if show_hist:
    display_msgs = st.session_state.messages
else:
    display_msgs = []   # nothing shown when unchecked

for msg in display_msgs:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if not display_msgs:
    st.markdown("""
        <div style="text-align:center; color:#ffffff; padding:8rem 1rem; font-size:1.4rem;">
            Ready when you are<br>
            <span style="font-size:1.1rem; opacity:0.8;">Memory is active. Ask anything.</span>
        </div>
    """, unsafe_allow_html=True)

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
