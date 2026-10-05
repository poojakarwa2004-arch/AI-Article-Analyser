import streamlit as st
import PyPDF2
from supabase import create_client
from openai import OpenAI

# -----------------------------
# PAGE CONFIGURATION
# -----------------------------
st.set_page_config(
    page_title="AI Article Analyser",
    page_icon="📰",
    layout="centered"
)

# -----------------------------
# CONNECTIONS
# -----------------------------
supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
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
# PROCESS ARTICLE
# -----------------------------
if uploaded_file is not None:

    st.success(f"Uploaded: {uploaded_file.name}")

    extracted_text = ""

    try:

        # PDF
        if uploaded_file.name.lower().endswith(".pdf"):

            pdf_reader = PyPDF2.PdfReader(uploaded_file)

            for page in pdf_reader.pages:

                page_text = page.extract_text()

                if page_text:
                    extracted_text += page_text + "\n"

        # TXT
        elif uploaded_file.name.lower().endswith(".txt"):

            extracted_text = uploaded_file.read().decode(
                "utf-8",
                errors="ignore"
            )

        # -----------------------------
        # CHECK TEXT
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
            # ANALYSE ARTICLE
            # -----------------------------
            if st.button(
                "🔍 Analyse Article",
                use_container_width=True
            ):

                try:

                    with st.spinner(
                        "🧠 Analysing the article..."
                    ):

                        # -----------------------------
                        # AI ANALYSIS
                        # -----------------------------
                        response = client.responses.create(
                            model="gpt-5-mini",
                            input=[
                                {
                                    "role": "system",
                                    "content": """
You are an economics tutor helping a first-year MBA student
understand economic news.

Analyse the article clearly and accurately.

Your response must contain:

1. ARTICLE SUMMARY
Explain what happened in simple language.

2. WHY IT MATTERS
Explain why this development is economically important.

3. KEY ECONOMIC CONCEPTS
Identify the relevant macroeconomic/economic concepts
and explain each one simply.

4. CAUSE AND EFFECT
Explain the main economic chain of events.

5. IMPACT
Discuss likely effects on:
- Inflation
- GDP/growth
- Employment
- Interest rates
- Government finances
- Businesses/consumers
Only discuss concepts that are actually relevant.

6. CRITICAL THINKING
Point out important assumptions, limitations, or questions
a reader should consider.

7. MBA TAKEAWAY
Give 3-5 things an MBA student should remember from this article.

Do not invent facts that are not present in the article.
Clearly distinguish between information stated in the article
and your own economic interpretation.
""",
                                },
                                {
                                    "role": "user",
                                    "content": extracted_text
                                }
                            ]
                        )

                        analysis = response.output_text

                    # -----------------------------
                    # DISPLAY ANALYSIS
                    # -----------------------------
                    st.success(
                        "✅ Article analysed successfully!"
                    )

                    st.subheader("🧠 Economic Analysis")

                    st.markdown(analysis)

                    # -----------------------------
                    # SAVE ANALYSIS
                    # -----------------------------
                    supabase.table("articles").update({
                        "analysis": analysis
                    }).eq(
                        "title",
                        uploaded_file.name
                    ).execute()

                    st.success(
                        "💾 Analysis saved to your article library."
                    )

                except Exception as e:

                    st.error(
                        f"Could not analyse the article: {e}"
                    )

        else:

            st.warning(
                "I couldn't extract any text from this file."
            )

            st.info(
                "If this is a scanned PDF, text extraction may "
                "not work yet."
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
