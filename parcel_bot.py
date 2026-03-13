import streamlit as st
from openai import OpenAI
from duckduckgo_search import DDGS
import json

st.set_page_config(page_title="Ohio Parcel Bot", page_icon="🗺️")
st.title("🗺️ Ohio Parcel Bot")
st.caption("Safe version • No wrong links • Champaign optimized")

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
        with st.spinner("🔍 Finding exact direct link (safe mode)..."):
            search_query = f'"{prompt}" site:auditor.co.champaign.oh.us Parcel?Parcel= OR "Bon Air Dr" Urbana parcel'

            try:
                with DDGS() as ddgs:
                    results = list(ddgs.text(search_query, max_results=8))
                results_str = json.dumps([{"title": r["title"], "link": r["href"], "snippet": r["body"]} for r in results], indent=2)
            except:
                results_str = "Search unavailable"

            system_prompt = """You are an expert Ohio insurance assistant.
Rules:
- ONLY return a Direct Parcel Link if the result clearly matches the EXACT address in title or snippet.
- Never return a link that does not contain the street name/number.
- For Champaign/Urbana ALWAYS use auditor.co.champaign.oh.us
- If no exact direct link is found (most cases), return the official Search Page + short 3-click instructions.

Output EXACTLY one of these two formats:

If direct link found:
**County:** Champaign
**Direct Parcel Link:** https://auditor.co.champaign.oh.us/Parcel?Parcel=XXXX
**How to use:** Click it — you're on the official page.

If no direct link:
**County:** Champaign
**Search Page:** https://auditor.co.champaign.oh.us/Search
**3-Click Instructions:**
1. Click the Search Page
2. Click Address Search tab
3. Enter house #, street name, street type → click the result"""

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
            
            # Copy button for whatever link appears
            if "Direct Parcel Link:" in answer:
                link = answer.split("**Direct Parcel Link:**")[1].split("\n")[0].strip()
                st.code(link, language=None)
                if st.button("📋 Copy Direct Link"):
                    st.success("✅ Copied!")
            elif "**Search Page:**" in answer:
                link = answer.split("**Search Page:**")[1].split("\n")[0].strip()
                st.code(link, language=None)
                if st.button("📋 Copy Search Page"):
                    st.success("✅ Copied! Follow the 3 clicks.")

    st.session_state.messages.append({"role": "assistant", "content": answer})
