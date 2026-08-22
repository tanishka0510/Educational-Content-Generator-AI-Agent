import streamlit as st
import requests

# -------------------------------------------------------
# Configuration
# -------------------------------------------------------

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Content Processing Agent",
    page_icon="📚",
    layout="wide"
)

# -------------------------------------------------------
# Header
# -------------------------------------------------------

st.title("📚 Content Processing Agent")
st.write(
    "Upload a document, process it, generate embeddings, "
    "store them in ChromaDB and perform semantic search."
)

st.divider()

# -------------------------------------------------------
# Upload Section
# -------------------------------------------------------

st.header("📄 Upload Document")

uploaded_file = st.file_uploader(
    "Choose a PDF",
    type=["pdf"]
)

if st.button("Upload & Process"):

    if uploaded_file is None:
        st.warning("Please select a PDF.")
    else:

        with st.spinner("Processing document..."):

            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file,
                    "application/pdf"
                )
            }

            response = requests.post(
                f"{BACKEND_URL}/upload/",
                files=files
            )

        if response.status_code == 200:

            data = response.json()

            st.success("Document processed successfully!")

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Chunks Created",
                    data["chunks_created"]
                )

            with col2:
                st.metric(
                    "Embedding Dimension",
                    data["embedding_dimension"]
                )

            st.info(f"Filename : {data['filename']}")
            st.info(f"File Type : {data['file_type']}")
            st.info(f"Status : {data['status']}")

        else:
            st.error(response.text)

st.divider()

# -------------------------------------------------------
# Search Section
# -------------------------------------------------------

st.header("🔍 Semantic Search")

query = st.text_input(
    "Enter your question"
)

top_k = st.slider(
    "Top K Results",
    1,
    10,
    5
)

if st.button("Search"):

    if query.strip() == "":
        st.warning("Enter a search query.")

    else:

        with st.spinner("Searching..."):

            response = requests.post(
                f"{BACKEND_URL}/search/",
                params={
                    "query": query,
                    "top_k": top_k
                }
            )

        if response.status_code == 200:

            data = response.json()

            st.success(
                f"Found {data['total_results']} results."
            )

            for i, result in enumerate(data["results"], start=1):

                with st.expander(f"Result {i}"):

                    st.write(
                        f"**Similarity Distance:** "
                        f"{result['distance']:.4f}"
                    )

                    metadata = result["metadata"]

                    st.write(
                        f"**Filename:** "
                        f"{metadata.get('filename','')}"
                    )

                    st.write(
                        f"**Subject:** "
                        f"{metadata.get('subject','')}"
                    )

                    st.write(
                        f"**Chunk:** "
                        f"{metadata.get('chunk_index','')}"
                    )

                    st.write("### Text")

                    st.write(result["text"])

        else:
            st.error(response.text)
    
st.divider()

# -------------------------------------------------------
# Footer
# -------------------------------------------------------

st.caption(
    "Educational Content Generator • Content Processing Agent"
)