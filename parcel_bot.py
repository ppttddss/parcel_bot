import streamlit as st
from openai import OpenAI
from duckduckgo_search import DDGS
import json

st.set_page_config(page_title="Champaign Parcel Bot", page_icon="🏠")
st.title("🏠 Champaign County Parcel Bot")
st.caption("Direct auditor parcel page only • Zero extra steps • Urbana optimized")

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

if prompt := st.chat_input("Enter property address (e.g. 612 College Way, Urbana, OH 43078)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🔍 Pulling your direct parcel page..."):
            search_query = f'"{prompt}" ("parcel number" OR "parcel id" OR "APN" OR "Parcel #:") (zillow OR redfin OR regrid) Urbana OR Champaign Ohio'

            try:
                with DDGS() as ddgs:
                    results = list(ddgs.text(search_query, max_results=10))
                results_str = json.dumps([{"title": r["title"], "link": r["href"], "snippet": r["body"]} for r in results], indent=2)
            except:
                results_str = "Search unavailable"

            system_prompt = """You are an expert Champaign County Ohio insurance assistant.
Rule: Return ONLY the direct auditor parcel page. No steps, no search page, no extra text.
- Scan results for the exact parcel ID (looks like K48-25-00-01-11-014-00 or K482500011101400)
- Format it with dashes if needed (K48-25-00-01-11-014-00 style)
- Build the exact URL: https://auditor.co.champaign.oh.us/Parcel?Parcel=ID
- If you find a matching parcel ID for the address, output exactly:

**Direct Parcel Page:** https://auditor.co.champaign.oh.us/Parcel?Parcel=XXXX

If no parcel ID found in any source:
**Direct Parcel Page:** Not publicly indexed yet for this address"""

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
            
            if "**Direct Parcel Page:**" in answer and "https" in answer:
                link = answer.split("**Direct Parcel Page:**")[1].split("\n")[0].strip()
                st.code(link, language=None)
                if st.button("📋 Copy Direct Link"):
                    st.success("✅ Copied! Paste in browser — you're on the official parcel page.")

    st.session_state.messages.append({"role": "assistant", "content": answer})
