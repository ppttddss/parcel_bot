import streamlit as st
from openai import OpenAI
from duckduckgo_search import DDGS
import json

st.set_page_config(page_title="Ohio Parcel Bot", page_icon="🗺️")
st.title("🗺️ Ohio County Auditor Parcel Bot")
st.caption("Now uses the REAL Champaign County site • Works for your Urbana addresses")

# API key
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

if prompt := st.chat_input("Enter any Ohio property address (e.g. 983 Bon Air Dr, Urbana, OH 43078)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🔍 Getting the correct search page + exact steps..."):
            search_query = f'"{prompt}" Ohio (auditor OR "county auditor") ("address search" OR "property search")'

            try:
                with DDGS() as ddgs:
                    results = list(ddgs.text(search_query, max_results=6))
                results_str = json.dumps([{"title": r["title"], "link": r["href"], "snippet": r["body"]} for r in results], indent=2)
            except:
                results_str = "Search unavailable"

            system_prompt = """You are an expert Ohio insurance assistant.
Special rule for Champaign County (any address with 'Urbana' or 'Champaign'):
- ALWAYS use https://auditor.co.champaign.oh.us/Search
- Give these EXACT 8-second steps
- Also give GIS map https://auditor.co.champaign.oh.us/Map

For ALL other counties use the search results.

Output EXACTLY:
**County:** ...
**Search Page:** https://...
**GIS Map (if available):** https://...
**8-Second Steps:**
1. Open the Search Page
2. Use "Address Search" section
3. House #: [number from address]
4. Street Name: [street]
5. Street Type: [Dr, St, Ave, etc.]
6. Click Search
7. Click the matching property → you get the direct parcel page like https://auditor.co.champaign.oh.us/Parcel?Parcel=...
**Bonus:** You will see tax value, owner, and everything you need."""

            full_prompt = f"Address: {prompt}\n\nSearch results:\n{results_str}"

            response = client.chat.completions.create(
                model="grok-4.20-beta-0309-non-reasoning",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.0,
                max_tokens=600
            )
            answer = response.choices[0].message.content.strip()

            st.markdown(answer)
            
            if "**Search Page:**" in answer:
                link = answer.split("**Search Page:**")[1].split("\n")[0].strip()
                st.code(link, language=None)
                if st.button("📋 Copy Search Page"):
                    st.success("✅ Copied! Now follow the 8-second steps.")

    st.session_state.messages.append({"role": "assistant", "content": answer})
