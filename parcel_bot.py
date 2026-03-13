import streamlit as st
from openai import OpenAI
from duckduckgo_search import DDGS
import json

st.set_page_config(page_title="Ohio Parcel + Photo Bot", page_icon="🏠")
st.title("🏠 Ohio Parcel + Photo Bot")
st.caption("All 88 counties • Direct links only • Accurate photos")

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

if prompt := st.chat_input("Enter any Ohio address (e.g. 3690 Rosedale Rd, Irwin, OH 43029)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🔍 Finding direct parcel + real photos..."):
            queries = [
                f'"{prompt}" ("parcel number" OR "parcel id" OR APN OR "Parcel #:") auditor Ohio',
                f'"{prompt}" zillow OR redfin',
                f'"{prompt}" site:.oh.us Parcel?Parcel='
            ]
            all_results = []
            for q in queries:
                try:
                    with DDGS() as ddgs:
                        results = list(ddgs.text(q, max_results=10))
                        all_results.extend(results)
                except:
                    pass
            results_str = json.dumps([{"title": r["title"], "link": r["href"], "snippet": r["body"]} for r in all_results], indent=2)

            system_prompt = """You are an expert Ohio insurance assistant.
For ANY Ohio address:
- First identify the county
- Find the official county auditor site (auditor.co.[county].oh.us)
- Extract the real parcel ID from Zillow/Redfin/auditor results
- Build the direct parcel URL: https://auditor.co.[county].oh.us/Parcel?Parcel=ID
- Also return correct Zillow, Redfin, and Google Maps Street View links
- Never invent links or ZPIDs

Output EXACTLY this format:

**Direct Parcel Page:** https://... (or "Not indexed yet")

**Zillow Photos:** https://...

**Redfin Photos:** https://...

**Google Street View:** https://www.google.com/maps/search/?api=1&query=[full address]"""

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
            
            # Auto copy buttons for every link
            for line in answer.splitlines():
                if "https://" in line and any(x in line for x in ["Parcel", "Zillow", "Redfin", "maps"]):
                    st.code(line.strip(), language=None)

    st.session_state.messages.append({"role": "assistant", "content": answer})
