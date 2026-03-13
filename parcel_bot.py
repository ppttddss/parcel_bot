import streamlit as st
import requests
import json
import os

st.set_page_config(page_title="Grok • SharePoint Team", page_icon="🟢", layout="centered")

st.title("🟢 Grok by xAI")
st.caption("Team Memory Active • NO history shown by default (clean view for SharePoint)")

# ================== API KEY FROM SECRETS ==================
api_key = st.secrets.get("XAI_API_KEY")
if not api_key:
    st.error("No API key in secrets. Add XAI_API_KEY in Streamlit Settings → Secrets")
    st.stop()

# ================== TEAM MEMORY FILE ==================
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

# Load full team memory (for Grok to learn from)
if "messages" not in st.session_state:
    st.session_state.messages = load_memory()

# Current session only (what is visible right now)
if "current_session" not in st.session_state:
    st.session_state.current_session = []

# Initial welcome in memory only (never shown unless you check the box)
if not st.session_state.messages:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi team! I'm Grok with permanent memory. Everything we talk about is remembered forever for the whole team."}
    ]
    save_memory(st.session_state.messages)

# ================== SIDEBAR CONTROLS ==================
with st.sidebar:
    st.success("✅ Team memory is ON (full history saved)")
    st.info(f"Total messages in team memory: {len(st.session_state.messages)}")
    
    show_last_20 = st.checkbox("Show last 20 team messages", value=False,
                               help="Check this to peek at the recent team history. Uncheck to go back to clean view.")
    
    if st.button("🗑️ Clear Team Memory", type="secondary"):
        if st.checkbox("Confirm: Delete ALL team history permanently"):
            st.session_state.messages = [
                {"role": "assistant", "content": "Team memory cleared. Starting fresh!"}
            ]
            st.session_state.current_session = []
            save_memory(st.session_state.messages)
            st.success("Team memory cleared!")
            st.rerun()

# ================== BUILD DISPLAY LIST ==================
display_messages = []
if show_last_20:
    display_messages = st.session_state.messages[-20:]   # last 20 from full team memory

display_messages += st.session_state.current_session     # always add this session's messages

# ================== DISPLAY MESSAGES ==================
for msg in display_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if not display_messages:
    st.info("Chat is clean (no history shown). Ask anything — team memory is still working in the background! 🚀")

# ================== USER INPUT ==================
if prompt := st.chat_input("Ask Grok anything (team memory active in background)..."):
    # Add to full memory + current session
    user_msg = {"role": "user", "content": prompt}
    st.session_state.messages.append(user_msg)
    st.session_state.current_session.append(user_msg)

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Grok is thinking (using full team memory)..."):
            recent_for_api = st.session_state.messages[-20:]  # API always sees last 20
            
            try:
                response = requests.post(
                    "https://api.x.ai/v1/chat/completions",
                    headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
                    json={
                        "model": "grok-4.20-beta-0309-non-reasoning",
                        "messages": [
                            {"role": "system", "content": "You are Grok, built by xAI. You have permanent memory of all previous team conversations. Be truthful, helpful, and witty."}
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
                error_msg = f"❌ API error: {str(e)}"
                st.error(error_msg)
                assistant_msg = {"role": "assistant", "content": error_msg}
                st.session_state.messages.append(assistant_msg)
                st.session_state.current_session.append(assistant_msg)

    # Save the full team memory after every reply
    save_memory(st.session_state.messages)

st.caption("Powered by xAI • Model: grok-4.20-beta-0309-non-reasoning • Shared team memory active (hidden by default)")
