import streamlit as st
from openai import OpenAI
from duckduckgo_search import DDGS
import json

st.set_page_config(page_title="Ohio Parcel Bot", page_icon="🗺️")
st.title("🗺️ Ohio Parcel Bot")
st.caption("NOW RETURNS DIRECT PARCEL LINKS • Champaign County optimized")

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

if prompt := st.chat_input("Enter address (e.g. 982 Bon Air Dr, Urbana, OH 43078)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🔍 Finding DIRECT parcel link..."):
            # Smart query that hits the real /Parcel?Parcel= pages
            if any(x in prompt.lower() for x in ["urbana", "champaign", "bon air"]):
                search_query = f'"{prompt}" site:auditor.co.champaign.oh.us "Parcel?Parcel=" OR parcel'
            else:
                search_query = f'"{prompt}" Ohio (auditor OR "county auditor") ("Parcel?Parcel=" OR parcel) site:.gov OR site:.us'

            try:
                with DDGS() as ddgs:
                    results = list(ddgs.text(search_query, max_results=8))
                results_str = json.dumps([{"title": r["title"], "link": r["href"], "snippet": r["body"]} for r in results], indent=2)
            except:
                results_str = "Search unavailable"

            system_prompt = """You are an expert Ohio insurance assistant.
Return the DIRECT parcel page if it exists (must contain /Parcel?Parcel= in the URL).
Only use the official auditor.co.champaign.oh.us site for Champaign/Urbana addresses.
If a direct link is found, use it. Never give the main Search page unless no direct link exists.
Output EXACTLY:
**County:** ...
**Direct Parcel Link:** https://... (the full Parcel?Parcel= link)
**How to use:** Just click it — you are on the official page with tax value, owner, photos, etc.
**Source:** one short line"""

            full_prompt = f"Address: {prompt}\n\nSearch results:\n{results_str}"

            response = client.chat.completions.create(
                model="grok-4.20-beta-0309-non-reasoning",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.0,
                max_tokens=400
            )
            answer = response.choices[0].message.content.strip()

            st.markdown(answer)
            
            if "**Direct Parcel Link:**" in answer:
                link = answer.split("**Direct Parcel Link:**")[1].split("\n")[0].strip()
                st.code(link, language=None)
                if st.button("📋 Copy Direct Link"):
                    st.success("✅ Copied! Paste in browser — you're there.")

    st.session_state.messages.append({"role": "assistant", "content": answer})
