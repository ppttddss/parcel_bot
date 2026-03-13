import streamlit as st
from openai import OpenAI
from duckduckgo_search import DDGS
import json

st.set_page_config(page_title="Ohio Parcel Bot", page_icon="🗺️")
st.title("🗺️ Ohio Parcel Bot")
st.caption("Correct Champaign County site • Shortest path to direct link")

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

if prompt := st.chat_input("Enter address (e.g. 983 Bon Air Dr, Urbana, OH 43078)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🔍 Getting you to the exact parcel page..."):
            # Hard-coded correct site for your county
            if "Urbana" in prompt or "Champaign" in prompt.lower():
                search_page = "https://auditor.co.champaign.oh.us/Search"
                gis_map = "https://auditor.co.champaign.oh.us/Map"
                county = "Champaign"
            else:
                search_query = f'"{prompt}" Ohio (auditor OR "county auditor") ("address search" OR "property search")'
                try:
                    with DDGS() as ddgs:
                        results = list(ddgs.text(search_query, max_results=5))
                    search_page = results[0]["href"] if results else "https://auditor.co.champaign.oh.us/Search"
                except:
                    search_page = "https://auditor.co.champaign.oh.us/Search"
                county = "Your county"

            system_prompt = """You are an expert Ohio insurance assistant.
For Champaign County (Urbana addresses) always use https://auditor.co.champaign.oh.us/Search
Give the shortest possible instructions (max 3 clicks) to reach the direct parcel page.
Output EXACTLY:
**County:** ...
**Search Page:** https://...
**GIS Map:** https://...
**3-Click Instructions:**
1. Open the Search Page
2. Click "Address Search"
3. Type the full address and click Search → click the matching result to get the direct parcel link[](https://auditor.co.champaign.oh.us/Parcel?Parcel=XXXX)"""

            full_prompt = f"Address: {prompt}\nCounty: {county}\nSearch Page: {search_page}"

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
            
            if "**Search Page:**" in answer:
                link = answer.split("**Search Page:**")[1].split("\n")[0].strip()
                st.code(link, language=None)
                if st.button("📋 Copy Search Page"):
                    st.success("✅ Copied! Now do the 3 clicks.")

    st.session_state.messages.append({"role": "assistant", "content": answer})
