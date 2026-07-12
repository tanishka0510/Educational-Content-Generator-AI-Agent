import streamlit as st
import requests

# ======================================================
# Page Configuration
# ======================================================

st.set_page_config(
    page_title="Document to Quiz Chatbot",
    page_icon="📄",
    layout="wide"
)

BACKEND_URL = "http://127.0.0.1:8000"

# ======================================================
# Session State
# ======================================================

if "uploaded" not in st.session_state:
    st.session_state.uploaded = False

if "filename" not in st.session_state:
    st.session_state.filename = ""

if "quiz" not in st.session_state:
    st.session_state.quiz = None

if "mode" not in st.session_state:
    st.session_state.mode = "chat"

if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "quiz_results" not in st.session_state:
    st.session_state.quiz_results = {}

# ======================================================
# Sidebar
# ======================================================

with st.sidebar:

    st.title("📄 Document")

    uploaded_file = st.file_uploader(
        "Upload PDF",
        type=["pdf"]
    )

    # Upload automatically after selecting a file
    if uploaded_file is not None and not st.session_state.uploaded:

        with st.spinner("Uploading document..."):

            response = requests.post(
                f"{BACKEND_URL}/upload",
                files={
                    "file": (
                        uploaded_file.name,
                        uploaded_file,
                        "application/pdf"
                    )
                }
            )

        if response.status_code == 200:

            data = response.json()

            st.session_state.uploaded = True
            st.session_state.filename = data["filename"]
            st.session_state.quiz = data["quiz"]["quiz"]
            st.session_state.quiz_results = {}

            st.success("✅ Document Uploaded")

            st.rerun()

        else:

            st.error("Upload Failed")

    st.divider()

    if st.session_state.uploaded:

        st.success(f"📄 {st.session_state.filename}")

        st.write("Choose an action:")

        if st.button("💬 Chat", use_container_width=True):
            st.session_state.mode = "chat"

        if st.button("📝 Generate Quiz", use_container_width=True):
            st.session_state.mode = "quiz"

# ======================================================
# Main Area
# ======================================================

st.title("📄 Document to Quiz Chatbot")

st.caption("Upload a PDF and interact with it.")

# ------------------------------------------------------
# Before Upload
# ------------------------------------------------------

if not st.session_state.uploaded:

    with st.chat_message("assistant"):

        st.markdown(
            """
### 👋 Welcome!

Upload a PDF from the left sidebar.

After uploading you can:

- 💬 Chat with the document
- 📝 Generate a Quiz
"""
        )

# ------------------------------------------------------
# Chat Mode
# ------------------------------------------------------

elif st.session_state.mode == "chat":

    st.subheader("💬 Chat with your Document")

    # Display previous conversation
    for message in st.session_state.messages:

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    question = st.chat_input("Ask anything about the uploaded document...")

    if question:

        # User message
        st.session_state.messages.append(
            {
                "role": "user",
                "content": question
            }
        )

        with st.chat_message("user"):
            st.markdown(question)

        with st.spinner("Thinking..."):

            response = requests.post(
                f"{BACKEND_URL}/chat",
                json={
                    "filename": st.session_state.filename,
                    "question": question
                }
            )

        if response.status_code == 200:

            answer = response.json()["answer"]

        else:

            answer = "Unable to generate response."

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        with st.chat_message("assistant"):
            st.markdown(answer)

# ------------------------------------------------------
# Quiz Mode
# ------------------------------------------------------

# ------------------------------------------------------
# Quiz Mode
# ------------------------------------------------------

elif st.session_state.mode == "quiz":

    if not st.session_state.quiz:

        st.info("No quiz available.")

    else:

        st.header("📝 Generated Quiz")

        for i, q in enumerate(st.session_state.quiz):

            st.subheader(f"Question {i+1}")

            st.write(q["question"])

            # -----------------------------
            # Find correct option
            # -----------------------------

            correct_option = next(
                option
                for option in q["options"]
                if option.startswith(q["answer"])
            )

            # -----------------------------
            # Question already answered
            # -----------------------------

            if i in st.session_state.quiz_results:

                result = st.session_state.quiz_results[i]

                st.radio(
                    "Choose your answer:",
                    q["options"],
                    index=q["options"].index(result["selected"]),
                    key=f"radio_{i}",
                    disabled=True
                )

                if result["correct"]:

                    st.success("✅ Correct!")

                else:

                    st.error("❌ Wrong!")

                    if result["show_answer"]:

                        st.info(f"✅ Correct Answer: {correct_option}")

                    else:

                        if st.button("Show Answer", key=f"show_{i}"):

                            st.session_state.quiz_results[i]["show_answer"] = True
                            st.rerun()

            # -----------------------------
            # Question not answered yet
            # -----------------------------

            else:

                selected = st.radio(
                    "Choose your answer:",
                    q["options"],
                    index=None,
                    key=f"radio_{i}"
                )

                if st.button("Submit", key=f"submit_{i}"):

                    if selected is None:

                        st.warning("Please select an option.")

                    else:

                        st.session_state.quiz_results[i] = {

                            "selected": selected,
                            "correct": selected == correct_option,
                            "show_answer": False

                        }

                        st.rerun()

            st.markdown("---")