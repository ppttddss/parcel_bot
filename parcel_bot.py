import streamlit as st
import requests
import json
import os

st.set_page_config(page_title="Grok • SharePoint Team", page_icon="🟢", layout="centered")

st.title("🟢 Grok by xAI")
st.caption("Team Memory Enabled — everyone shares the same history")

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

# Load shared team memory
if "messages" not in st.session_state:
    st.session_state.messages = load_memory()

# Initial welcome if empty
if not st.session_state.messages:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi team! I'm Grok with permanent memory. Everything we talk about here is remembered for the whole team. Ask me anything! 🚀"}
    ]
    save_memory(st.session_state.messages)

# ================== DISPLAY MESSAGES ==================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ================== USER INPUT ==================
if prompt := st.chat_input("Ask Grok anything (team memory is active)..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Grok is thinking (using team memory)..."):
            # Trim to last 20 messages for the API (keeps context safe)
            recent_messages = st.session_state.messages[-20:]
            
            try:
                response = requests.post(
                    "https://api.x.ai/v1/chat/completions",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {api_key}"
                    },
                    json={
                        "model": "grok-4.20-beta-0309-non-reasoning",   # Latest March 2026 model
                        "messages": [
                            {"role": "system", "content": "You are Grok, built by xAI. You have permanent memory of all previous team conversations. Be truthful, helpful, and witty."}
                        ] + recent_messages
                    },
                    timeout=90
                )
                response.raise_for_status()
                reply = response.json()["choices"][0]["message"]["content"]
                
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.markdown(reply)
                
            except Exception as e:
                error_msg = f"❌ API error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

    # Save the updated team memory after every reply
    save_memory(st.session_state.messages)

# ================== SIDEBAR CONTROLS ==================
with st.sidebar:
    st.success("✅ Team memory is ON")
    st.info(f"Total messages saved: {len(st.session_state.messages)}")
    
    if st.button("🗑️ Clear Team Memory", type="secondary"):
        if st.checkbox("I understand this will delete ALL team history permanently"):
            st.session_state.messages = [
                {"role": "assistant", "content": "Team memory has been cleared. Starting fresh! 🚀"}
            ]
            save_memory(st.session_state.messages)
            st.success("Team memory cleared!")
            st.rerun()

st.caption("Powered by xAI • Model: grok-4.20-beta-0309-non-reasoning • Shared team memory active")
