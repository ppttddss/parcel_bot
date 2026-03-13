import streamlit as st
import requests

st.set_page_config(page_title="Grok • SharePoint", page_icon="🟢", layout="centered")

st.title("🟢 Grok by xAI")
st.caption("Live chat — embedded in SharePoint")

# === API KEY (sidebar) ===
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

api_key = st.sidebar.text_input(
    "xAI API Key",
    type="password",
    value=st.session_state.api_key,
    placeholder="xai-...",
    help="Get it free at https://console.x.ai"
)

if api_key:
    st.session_state.api_key = api_key
else:
    st.warning("Enter your xAI API key in the sidebar to start")
    st.stop()

# === CHAT HISTORY ===
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I'm Grok, built by xAI. Ask me anything — I'm ready inside SharePoint! 🚀"}
    ]

# Display messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
if prompt := st.chat_input("Ask Grok anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Grok is thinking..."):
            try:
                response = requests.post(
                    "https://api.x.ai/v1/chat/completions",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {api_key}"
                    },
                    json={
                        "model": "grok-4.20-beta-latest-non-reasoning",
                        "messages": [
                            {"role": "system", "content": "You are Grok, built by xAI. Be maximally truthful, helpful, and a bit witty."}
                        ] + st.session_state.messages
                    },
                    timeout=60
                )
                response.raise_for_status()
                reply = response.json()["choices"][0]["message"]["content"]
                
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.markdown(reply)
                
            except Exception as e:
                error = f"❌ API error: {str(e)}\n\nCheck your key/quota at console.x.ai"
                st.error(error)
                st.session_state.messages.append({"role": "assistant", "content": error})

st.caption("Powered by xAI • Model: grok-4.20-beta-latest-non-reasoning")
