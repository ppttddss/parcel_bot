import streamlit as st
from openai import OpenAI
from duckduckgo_search import DDGS
import json

st.set_page_config(page_title="Ohio Parcel Bot", page_icon="🗺️")
st.title("🗺️ Ohio County Auditor Parcel Bot")
st.caption("Now gives exact search instructions • Powered by Grok")

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

if prompt := st.chat_input("Enter any Ohio property address (e.g. 123 Main St, Urbana, OH 43078)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🔍 Getting the exact search page + instructions..."):
            search_query = f'"{prompt}" Ohio (auditor OR "county auditor") ("property search" OR "parcel search" OR "address search") site:.gov OR site:.us'

            try:
                with DDGS() as ddgs:
                    results = list(ddgs.text(search_query, max_results=8))
                results_str = json.dumps([{"title": r["title"], "link": r["href"], "snippet": r["body"]} for r in results], indent=2)
            except:
                results_str = "Search unavailable"

            system_prompt = """You are an expert Ohio insurance assistant.
For the address:
- Identify the county
- Return the official county auditor property SEARCH page (usually ends in /Search)
- If a direct parcel permalink exists, use it
- Otherwise (most counties) give the search page + CLEAR step-by-step instructions

Output EXACTLY this format:
**County:** ...
**Main Search Page:** https://...
**Direct Parcel Link (if available):** https://... or "None - use the steps below"
**Step-by-step instructions:**
1. Open the Main Search Page link
2. [exact steps for this county, e.g. Type the full address in the search bar]
3. Click the matching property
**Bonus:** GIS Map link if available
**Why correct:** one short sentence"""

            full_prompt = f"Address: {prompt}\n\nSearch results:\n{results_str}"

            response = client.chat.completions.create(
                model="grok-4.20-beta-0309-non-reasoning",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.0,
                max_tokens=500
            )
            answer = response.choices[0].message.content.strip()

            st.markdown(answer)
            
            if "Main Search Page:" in answer:
                link = answer.split("Main Search Page:")[1].split("\n")[0].strip()
                st.code(link, language=None)
                if st.button("📋 Copy Search Page Link"):
                    st.success("✅ Copied!")

    st.session_state.messages.append({"role": "assistant", "content": answer})
