import streamlit as st
import PyPDF2
from supabase import create_client

# -----------------------------
# SUPABASE CONNECTION
# -----------------------------
supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

# -----------------------------
# PAGE CONFIGURATION
# -----------------------------
st.set_page_config(
    page_title="AI Article Analyser",
    page_icon="📰",
    layout="centered"
)

# -----------------------------
# TITLE
# -----------------------------
st.title("📰 AI Article Analyser")

st.markdown(
    """
    ### Turn news into economic understanding.

    Upload an Economic Times article and use this tool to
    understand the article, its economic context, and the
    macroeconomic concepts behind it.
    """
)

st.divider()

# -----------------------------
# WHAT THE APP WILL DO
# -----------------------------
st.subheader("What can you do here?")

st.markdown(
    """
    - 📄 Upload a news article
    - 🧠 Understand the article in simple language
    - 📊 Identify relevant macroeconomic concepts
    - 🌍 Understand the broader economic context
    - 🔎 Critically analyse the article
    - 📰 Connect the article with current developments
    """
)

st.divider()

# -----------------------------
# ARTICLE UPLOAD
# -----------------------------
st.subheader("📄 Upload Article")

uploaded_file = st.file_uploader(
    "Choose an article in PDF or TXT format",
    type=["pdf", "txt"]
)

# -----------------------------
# PROCESS UPLOADED FILE
# -----------------------------
if uploaded_file is not None:

    st.success(f"Uploaded: {uploaded_file.name}")

    extracted_text = ""

    try:

        # -----------------------------
        # PDF
        # -----------------------------
        if uploaded_file.name.lower().endswith(".pdf"):

            pdf_reader = PyPDF2.PdfReader(uploaded_file)

            for page in pdf_reader.pages:

                page_text = page.extract_text()

                if page_text:
                    extracted_text += page_text + "\n"

        # -----------------------------
        # TXT
        # -----------------------------
        elif uploaded_file.name.lower().endswith(".txt"):

            extracted_text = uploaded_file.read().decode(
                "utf-8",
                errors="ignore"
            )

        # -----------------------------
        # CHECK EXTRACTED TEXT
        # -----------------------------
        if extracted_text.strip():

            st.subheader("📖 Article Preview")

            with st.expander("Click to view the extracted article"):

                st.text_area(
                    "Article text",
                    extracted_text,
                    height=400,
                    label_visibility="collapsed"
                )

            st.divider()

            # -----------------------------
            # SAVE ARTICLE
            # -----------------------------
            if st.button(
                "🔍 Analyse Article",
                use_container_width=True
            ):

                try:

                    # Save article to Supabase
                    response = supabase.table("articles").insert({
                        "title": uploaded_file.name,
                        "source": "Economic Times",
                        "article_text": extracted_text,
                        "analysis": ""
                    }).execute()

                    st.success(
                        "✅ Article saved successfully!"
                    )

                    st.info(
                        """
                        Your article has been saved to your
                        personal article library.

                        AI analysis will be added next.
                        """
                    )

                except Exception as e:

                    st.error(
                        f"Could not save the article: {e}"
                    )

        else:

            st.warning(
                "I couldn't extract any text from this file."
            )

            st.info(
                "If this is a scanned PDF, text extraction "
                "may not work yet."
            )

    except Exception as e:

        st.error(
            f"Something went wrong while reading the file: {e}"
        )

# -----------------------------
# FOOTER
# -----------------------------
st.divider()

st.caption(
    "AI Article Analyser • Built for daily economic news reading"
)
