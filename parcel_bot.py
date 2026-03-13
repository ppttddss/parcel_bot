import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Ask Grok", page_icon="🚀")
st.title("🚀 Ask Grok")
st.caption("Powered by xAI • Your personal Grok right in SharePoint")

if "XAI_API_KEY" in st.secrets:
    api_key = st.secrets["XAI_API_KEY"]
else:
    api_key = st.sidebar.text_input("Your xAI API Key", type="password")

if not api_key:
    st.error("Add your key in Secrets or sidebar")
    st.stop()

client = OpenAI(base_url="https://api.x.ai/v1", api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask me anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = client.chat.completions.create(
                model="grok-4.20-beta-0309-non-reasoning",
                messages=[
                    {"role": "system", "content": "You are Grok, built by xAI. Be helpful, truthful, and a little witty."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            answer = response.choices[0].message.content.strip()
            st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
