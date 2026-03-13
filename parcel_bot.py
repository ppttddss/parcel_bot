import streamlit as st
from openai import OpenAI
from duckduckgo_search import DDGS
import json

st.set_page_config(page_title="Ohio Parcel Bot", page_icon="🗺️")
st.title("🗺️ Ohio County Auditor Parcel Link Bot")
st.caption("Powered by Grok 4.20 • For insurance agents in Ohio")

# Sidebar for API key
api_key = st.sidebar.text_input("Your xAI API Key", type="password", value=st.session_state.get("xai_key", ""))

if api_key:
    st.session_state.xai_key = api_key

client = OpenAI(base_url="https://api.x.ai/v1", api_key=api_key) if api_key else None

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Enter any Ohio property address (e.g. 123 Main St, Urbana, OH 43078)"):
    if not api_key:
        st.error("Paste your xAI API key in the sidebar first!")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🔍 Searching official county auditor records..."):
            search_query = f'"{prompt}" Ohio (auditor OR "county auditor") (parcel OR property OR "tax record") site:.gov OR site:.us'
            
            try:
                with DDGS() as ddgs:
                    results = list(ddgs.text(search_query, max_results=8))
                results_str = json.dumps([{"title": r["title"], "link": r["href"], "snippet": r["body"]} for r in results], indent=2)
            except:
                results_str = "Search results unavailable right now"

            system_prompt = """You are an expert Ohio insurance assistant.
Return ONLY the most direct official county auditor parcel page for the given address.
Rules:
- Prefer exact parcel permalink on auditor.*.oh.us or official county .gov
- If only a search page, return that + exact instructions
- Never guess or invent links
Output format exactly:
**Direct Parcel Link:** https://...
**County:** ...
**How to use:** 1-2 short sentences
**Source:** why this link is correct"""

            full_prompt = f"Address: {prompt}\n\nFresh search results:\n{results_str}"

            response = client.chat.completions.create(
                model="grok-4.20-beta-latest-non-reasoning",   # ← Current 2026 model
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.0,
                max_tokens=400
            )
            answer = response.choices[0].message.content.strip()

            st.markdown(answer)
            
            # Auto copy button
            if "**Direct Parcel Link:**" in answer:
                link = answer.split("**Direct Parcel Link:**")[1].split("\n")[0].strip()
                st.code(link, language=None)
                if st.button("📋 Copy Link to Clipboard"):
                    st.success("Link copied!")

    st.session_state.messages.append({"role": "assistant", "content": answer})