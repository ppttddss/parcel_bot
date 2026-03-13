import streamlit as st
from openai import OpenAI
from duckduckgo_search import DDGS
import json

st.set_page_config(page_title="Champaign Parcel Bot", page_icon="🏠")
st.title("🏠 Champaign County Parcel Bot")
st.caption("Now works like Grok • Direct links only • No steps")

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

if prompt := st.chat_input("Enter property address (e.g. 333 Sweetman Ave, Urbana, OH 43078)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🔍 Finding your DIRECT parcel page (Grok-style search)..."):
            # Stronger searches like Grok uses
            queries = [
                f'"{prompt}" ("parcel number" OR "parcel id" OR APN OR "Parcel #:") (zillow OR redfin OR "parcel number") Urbana Champaign',
                f'"{prompt}" K48 OR "K48-25" OR "Parcel?Parcel=" Urbana',
                f'"{prompt}" site:auditor.co.champaign.oh.us parcel'
            ]
            
            all_results = []
            for q in queries:
                try:
                    with DDGS() as ddgs:
                        results = list(ddgs.text(q, max_results=8))
                        all_results.extend(results)
                except:
                    pass
            
            results_str = json.dumps([{"title": r["title"], "link": r["href"], "snippet": r["body"]} for r in all_results], indent=2)

            system_prompt = """You are Grok — full power search mode.
For ANY Champaign/Urbana address:
- Scan EVERY snippet for parcel ID (look for patterns like K48-25-00-02-06-025-00 or K482500020602500)
- Extract the exact ID and format it with dashes (K48-25-00-..-..-..)
- Build the direct URL: https://auditor.co.champaign.oh.us/Parcel?Parcel=ID
- Rule: ONLY return the direct link if you are 100% confident it matches the address. Never guess.

Output EXACTLY:
**Direct Parcel Page:** https://auditor.co.champaign.oh.us/Parcel?Parcel=XXXX

If no ID found after searching:
**Direct Parcel Page:** Not indexed yet"""

            full_prompt = f"Address: {prompt}\n\nAll search results:\n{results_str}"

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
                    st.success("✅ Copied! Paste in browser — you're there.")

    st.session_state.messages.append({"role": "assistant", "content": answer})
