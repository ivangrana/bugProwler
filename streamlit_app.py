# streamlit_app.py
import json

import streamlit as st

from src.app.agent import agno_assist  # import your BugProwler agent
from src.app.markdown_idor import generate_markdown
from src.app.swagger_analysis import IDORAnalyzer

st.set_page_config(page_title="BugProwler Agent", layout="wide")

st.title("𖢥 BugProwler")

# ---------- sidebar navigation ----------
with st.sidebar:
    st.markdown("### Toolbox:")
    chat_btn = st.button("Chat", key="chat_btn")
    swagger_btn = st.button("Swagger Docs Analyzer", key="swagger_btn")

    if "page" not in st.session_state:
        st.session_state.page = "Chat"

    if chat_btn:
        st.session_state.page = "Chat"
    if swagger_btn:
        st.session_state.page = "Swagger Docs Analyzer"

page = st.session_state.page

# ---------- session state ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "swagger_analysis" not in st.session_state:
    st.session_state.swagger_analysis = []

if page == "Chat":
    # ---------- display history ----------
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # ---------- file uploader ----------
    uploaded_file = st.file_uploader(
        "Upload a file...", type=["txt", "md", "csv", "json", "png", "jpg", "jpeg"]
    )
    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        st.write("File uploaded successfully!")
        # Optional: display the file contents if it's text
        if uploaded_file.type.startswith("text") or uploaded_file.type in [
            "application/json"
        ]:
            try:
                content_str = file_bytes.decode("utf-8")
                st.code(content_str)
            except Exception as e:
                st.write(f"Unable to display file contents: {e}")

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

elif page == "Swagger Docs Analyzer":
    st.header("Swagger/OpenAPI Docs Analyzer")
    swagger_file = st.file_uploader(
        "Upload a Swagger/OpenAPI JSON or YAML file", type=["json", "yaml", "yml"]
    )
    if swagger_file is not None:
        try:
            file_bytes = swagger_file.read()
            # Try to decode as UTF-8 text
            content_str = file_bytes.decode("utf-8")
            # st.code(
            #     content_str,
            #     language="yaml"
            #     if swagger_file.type.endswith("yaml")
            #     or swagger_file.type.endswith("yml")
            #     else "json",
            # )
            # Ask the agent to analyze the Swagger docs
            analyze_prompt = f"Analyze the following Swagger/OpenAPI specification and summarize its endpoints, authentication, and notable features:\n\n{content_str}"
            with st.spinner("Analyzing Swagger/OpenAPI docs..."):
                analyzer = IDORAnalyzer()
                spec = analyzer.analyze_file_bytes(file_bytes)
                st.success("Analysis completed")
                st.markdown(generate_markdown(spec))
        except Exception as e:
            st.error(f"Error reading or analyzing Swagger/OpenAPI file: {e}")

    # Display previous analyses
    if st.session_state.swagger_analysis:
        st.subheader("Previous Swagger/OpenAPI Analyses")
        for entry in st.session_state.swagger_analysis:
            st.markdown(f"**{entry['file']}**")
            st.markdown(entry["analysis"])
