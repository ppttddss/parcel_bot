import streamlit as st
from openai import OpenAI
from duckduckgo_search import DDGS
import json

st.set_page_config(page_title="Ohio Parcel Bot", page_icon="🗺️")
st.title("🗺️ Ohio Parcel Bot")
st.caption("DIRECT LINK ONLY • Zillow trick added • No steps ever")

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

if prompt := st.chat_input("Enter address (e.g. 612 College Way, Urbana, OH 43078)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🔍 Finding your DIRECT parcel link..."):
            search_query = f'"{prompt}" (parcel OR "parcel number" OR "parcel id" OR "Parcel #:") (zillow OR redfin OR auditor) Urbana OR Champaign'

            try:
                with DDGS() as ddgs:
                    results = list(ddgs.text(search_query, max_results=10))
                results_str = json.dumps([{"title": r["title"], "link": r["href"], "snippet": r["body"]} for r in results], indent=2)
            except:
                results_str = "Search unavailable"

            system_prompt = """You are an expert Ohio insurance assistant.
Rule #1: ONLY return a direct link if you find the real parcel ID. NO steps, NO search page, NO extra words.
For Champaign County:
- Scan Zillow/Redfin snippets for "Parcel number :" or "Parcel #:" or "Parcel ID:"
- Extract the exact parcel ID (format it as K48-25-00-..-..-.. if needed)
- Build the full direct URL: https://auditor.co.champaign.oh.us/Parcel?Parcel=ID
- If found, output ONLY this format:

**Direct Parcel Link:** https://auditor.co.champaign.oh.us/Parcel?Parcel=XXXX

If no parcel ID found anywhere: 
**Direct Parcel Link not indexed yet**"""

            full_prompt = f"Address: {prompt}\n\nSearch results:\n{results_str}"

            response = client.chat.completions.create(
                model="grok-4.20-beta-0309-non-reasoning",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.0,
                max_tokens=300
            )
            answer = response.choices[0].message.content.strip()

            st.markdown(answer)
            
            if "**Direct Parcel Link:**" in answer:
                link = answer.split("**Direct Parcel Link:**")[1].split("\n")[0].strip()
                st.code(link, language=None)
                if st.button("📋 Copy Direct Link"):
                    st.success("✅ Copied! Paste in browser — you're there.")

    st.session_state.messages.append({"role": "assistant", "content": answer})
