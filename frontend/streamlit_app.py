# frontend/streamlit_app.py
import streamlit as st
import httpx
import json

API = "http://127.0.0.1:8000"

st.set_page_config(page_title="Email Agent", layout="wide")
st.title("Prompt-Driven Email Productivity Agent (file storage)")

with st.sidebar:
    st.header("Setup")
    if st.button("Load Mock Inbox"):
        data = json.load(open("assets/mock_inbox.json"))
        st.write(httpx.post(f"{API}/load_mock", json=data).json())
    if st.button("Load Default Prompts"):
        data = json.load(open("assets/default_prompts.json"))
        for p in data["prompts"]:
            httpx.post(f"{API}/prompts", json=p)
        st.success("Prompts loaded")

cols = st.columns([1,2,2])

with cols[0]:
    st.subheader("Inbox")
    emails = httpx.get(f"{API}/emails").json()
    for e in emails:
        btn = st.button(f'{e["id"]} | {e["sender"]} | {e["subject"]}', key=f"e{e['id']}")
        if btn:
            st.session_state['sel'] = e['id']

with cols[1]:
    st.subheader("Email Viewer")
    sel = st.session_state.get("sel")
    if sel:
        emails = httpx.get(f"{API}/emails").json()
        email = next((x for x in emails if x["id"] == sel), None)
        if email:
            st.write("**From:**", email["sender"])
            st.write("**Subject:**", email["subject"])
            st.write(email["body"])
            if st.button("Process (Categorize + Extract)"):
                st.write(httpx.post(f"{API}/process/{sel}").json())

with cols[2]:
    st.subheader("Agent Chat")
    sel = st.session_state.get("sel")
    prompt_choice = st.selectbox("Prompt (optional)", ["", "Categorize Emails", "Action Item Extraction", "Auto-Reply Draft"])
    question = st.text_area("Ask the agent (e.g., Summarize, Draft reply)")
    if st.button("Run Agent"):
        if not sel:
            st.warning("Select an email first")
        else:
            payload = {"email_id": sel, "prompt_name": prompt_choice or None, "user_query": question}
            st.write(httpx.post(f"{API}/agent/query", json=payload).json())

st.markdown("---")
st.subheader("Drafts")
if st.button("Create test draft for selected email"):
    sel = st.session_state.get("sel")
    if not sel:
        st.warning("Select email")
    else:
        payload = {"email_id": sel, "subject": "Draft subject", "body": "Draft body", "metadata": {}}
        st.write(httpx.post(f"{API}/draft", json=payload).json())
