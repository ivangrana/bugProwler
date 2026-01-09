# streamlit_app.py
import streamlit as st
from src.app.agent import agno_assist  # 1️⃣ import your AgentOS agent

st.set_page_config(page_title="AgentOS ↔ Streamlit", layout="centered")
st.title("🤖 AgentOS Chat")

# ---------- session state ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------- display history ----------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------- input ----------
if prompt := st.chat_input("Ask me anything…"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # ---------- run agent ----------
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full = ""
        for chunk in agno_assist.run(
            prompt, stream=True, debug_mode=True
        ):  # 2️⃣ streaming straight into UI
            if chunk.content:
                full += chunk.content
                placeholder.markdown(full + "▌")
        placeholder.markdown(full)
    st.session_state.messages.append({"role": "assistant", "content": full})
