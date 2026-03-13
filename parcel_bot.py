import streamlit as st
from openai import OpenAI
from duckduckgo_search import DDGS
import json

st.set_page_config(page_title="Ohio Parcel Bot", page_icon="🗺️")
st.title("🗺️ Ohio Parcel Bot")
st.caption("Direct links when possible • Champaign/Urbana optimized • No wrong links")

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

if prompt := st.chat_input("Enter any Ohio address (e.g. 612 College Way, Urbana, OH 43078)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🔍 Looking for your direct parcel link..."):
            # Super-targeted search for Champaign County
            if any(word in prompt.lower() for word in ["urbana", "champaign", "bon air", "college way"]):
                search_query = f'"{prompt}" site:auditor.co.champaign.oh.us ("Parcel?Parcel=" OR parcel)'
            else:
                search_query = f'"{prompt}" Ohio auditor ("Parcel?Parcel=" OR parcel)'

            try:
                with DDGS() as ddgs:
                    results = list(ddgs.text(search_query, max_results=8))
                results_str = json.dumps([{"title": r["title"], "link": r["href"], "snippet": r["body"]} for r in results], indent=2)
            except:
                results_str = "Search unavailable"

            system_prompt = """You are an expert Ohio insurance assistant.
For Champaign County addresses:
- ONLY return a Direct Parcel Link if the result contains the exact house number AND street name in the title or snippet.
- Never return a wrong link.
- If no exact direct link is found, return the official Search Page + 3-click instructions.

Output EXACTLY:
If direct link found:
**County:** Champaign
**Direct Parcel Link:** https://auditor.co.champaign.oh.us/Parcel?Parcel=XXXX
**How to use:** Click it — you're on the official page with owner, value, taxes, etc.

If no direct link:
**County:** Champaign
**Search Page:** https://auditor.co.champaign.oh.us/Search
**3-Click Instructions:**
1. Open the Search Page
2. Click "Address Search"
3. Enter house number, street name, street type → click the matching result (takes 8 seconds)"""

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
                    st.success("✅ Copied!")
            else:
                link = answer.split("**Search Page:**")[1].split("\n")[0].strip()
                st.code(link, language=None)
                if st.button("📋 Copy Search Page"):
                    st.success("✅ Copied! Follow the 3 clicks.")

    st.session_state.messages.append({"role": "assistant", "content": answer})
