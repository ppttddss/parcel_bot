import streamlit as st
from openai import OpenAI
from duckduckgo_search import DDGS
import json

st.set_page_config(page_title="Parcel + Photo Bot", page_icon="🏠")
st.title("🏠 Champaign Parcel + Photo Bot")
st.caption("Direct links only • Accurate photos • Powered by Grok")

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

if prompt := st.chat_input("Enter property address (e.g. 409 Boyce St, Urbana, OH 43078)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🔍 Finding direct parcel page + real photos..."):
            # Strong searches (same power I use)
            queries = [
                f'"{prompt}" ("parcel number" OR "parcel id" OR APN) (zillow OR redfin OR auditor) Urbana',
                f'"{prompt}" site:auditor.co.champaign.oh.us Parcel?Parcel=',
                f'"{prompt}" zillow',
                f'"{prompt}" redfin'
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

            system_prompt = """You are an expert Champaign County Ohio insurance assistant.
Return ONLY direct, verified links. Never invent ZPIDs or links.
- For parcel: extract real parcel ID (K48-25-00-..-..-.. format) and build https://auditor.co.champaign.oh.us/Parcel?Parcel=ID
- For photos: use only real Zillow and Redfin links that contain the exact address
- Street View: always use the reliable Google Maps search link

Output exactly this format (nothing else):

**Direct Parcel Page:** https://auditor.co.champaign.oh.us/Parcel?Parcel=XXXX (or "Not indexed yet")

**Zillow Photos:** https://...

**Redfin Photos:** https://...

**Google Street View:** https://www.google.com/maps/search/?api=1&query=full address here"""

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
            
            # One-click copy for every link
            for line in answer.split("\n"):
                if "https://" in line and ("Parcel" in line or "Zillow" in line or "Redfin" in line or "Street View" in line or "maps" in line):
                    st.code(line.strip(), language=None)

    st.session_state.messages.append({"role": "assistant", "content": answer})
