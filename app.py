import streamlit as st
import PyPDF2
import time
from supabase import create_client
from google import genai


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Article Analyser",
    page_icon="📰",
    layout="centered"
)


# ============================================================
# CONNECTIONS
# ============================================================

supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

gemini_client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)


# ============================================================
# TITLE
# ============================================================

st.title("📰 AI Article Analyser")

st.markdown(
    """
    ### Turn news into economic understanding.

    Upload an Economic Times article and use this tool to
    understand the article, its economic context, and the
    economic concepts behind it.
    """
)

st.divider()


# ============================================================
# FEATURES
# ============================================================

st.subheader("What can you do here?")

st.markdown(
    """
    - 📄 Upload a news article
    - 🧠 Understand the article in simple language
    - 📊 Identify relevant economic concepts
    - 🌍 Understand the broader economic context
    - 🔎 Critically analyse the article
    - 🎓 Extract MBA-level takeaways
    """
)

st.divider()


# ============================================================
# ARTICLE UPLOAD
# ============================================================

st.subheader("📄 Upload Article")

uploaded_file = st.file_uploader(
    "Choose an article in PDF or TXT format",
    type=["pdf", "txt"]
)


# ============================================================
# PROCESS ARTICLE
# ============================================================

if uploaded_file is not None:

    st.success(f"Uploaded: {uploaded_file.name}")

    extracted_text = ""

    try:

        # ----------------------------------------------------
        # EXTRACT PDF TEXT
        # ----------------------------------------------------

        if uploaded_file.name.lower().endswith(".pdf"):

            pdf_reader = PyPDF2.PdfReader(uploaded_file)

            for page in pdf_reader.pages:

                page_text = page.extract_text()

                if page_text:
                    extracted_text += page_text + "\n"


        # ----------------------------------------------------
        # EXTRACT TXT
        # ----------------------------------------------------

        elif uploaded_file.name.lower().endswith(".txt"):

            extracted_text = uploaded_file.read().decode(
                "utf-8",
                errors="ignore"
            )


        # ----------------------------------------------------
        # CHECK TEXT
        # ----------------------------------------------------

        if not extracted_text.strip():

            st.warning(
                "I couldn't extract any text from this file."
            )

            st.info(
                "If this is a scanned PDF, text extraction "
                "may not work yet."
            )

        else:

            # ------------------------------------------------
            # ARTICLE PREVIEW
            # ------------------------------------------------

            st.subheader("📖 Article Preview")

            with st.expander(
                "Click to view the extracted article"
            ):

                st.text_area(
                    "Article text",
                    extracted_text,
                    height=400,
                    label_visibility="collapsed"
                )

            st.divider()


            # =================================================
            # ANALYSE BUTTON
            # =================================================

            if st.button(
                "🔍 Analyse Article",
                use_container_width=True
            ):

                try:

                    # =========================================
                    # SAVE ARTICLE
                    # =========================================

                    with st.spinner(
                        "💾 Saving article..."
                    ):

                        article_data = {
                            "title": uploaded_file.name,
                            "source": "Economic Times",
                            "article_text": extracted_text,
                            "analysis": ""
                        }

                        supabase.table(
                            "articles"
                        ).insert(
                            article_data
                        ).execute()

                    st.success(
                        "✅ Article saved successfully!"
                    )


                    # =========================================
                    # AI ANALYSIS
                    # =========================================

                    with st.spinner(
                        "🧠 Analysing the article..."
                    ):

                        prompt = f"""
You are an economics tutor helping a first-year MBA student
understand economic news.

Analyse the article clearly, accurately and educationally.

ARTICLE:

{extracted_text}


Your response must contain:

## 1. ARTICLE SUMMARY

Explain what happened in simple language.

Include:
- What happened?
- Who is involved?
- What is changing?
- Important numbers or facts.


## 2. WHY IT MATTERS

Explain why the development is economically important.


## 3. KEY ECONOMIC CONCEPTS

Identify the economic concepts relevant to the article.

For every concept:
- Name the concept
- Explain it simply
- Explain how it appears in this article

Only include genuinely relevant concepts.


## 4. CAUSE AND EFFECT

Explain the economic chain step by step.

Use arrows where useful.

Example:

Higher oil prices
→ higher input costs
→ higher transportation costs
→ higher prices
→ inflationary pressure


## 5. IMPACT ON THE ECONOMY

Discuss only relevant areas:

- Inflation
- GDP / economic growth
- Employment
- Interest rates
- Government finances
- Businesses
- Consumers
- Investment
- Trade
- Currency / exchange rates


## 6. CRITICAL THINKING

Give 3–5 questions or limitations an MBA student
should consider.

Think about:
- Assumptions
- Winners and losers
- Missing information
- Alternative explanations
- What could happen next


## 7. MBA TAKEAWAY

Give 3–5 concise points an MBA student should remember.


IMPORTANT:

1. Do not invent facts.
2. Do not invent statistics.
3. Clearly distinguish article facts from interpretation.
4. Explain technical economic terminology simply.
5. Do not discuss unrelated economic concepts.
"""


                        # =====================================
                        # GEMINI WITH RETRIES
                        # =====================================

                        analysis = None
                        last_error = None

                        for attempt in range(3):

                            try:

                                response = (
                                    gemini_client.models.generate_content(
                                        model="gemini-3.8-flash",
                                        contents=prompt
                                    )
                                )

                                analysis = response.text
                                break

                            except Exception as e:

                                last_error = e

                                if attempt < 2:

                                    time.sleep(5)

                                else:

                                    raise last_error


                    # =========================================
                    # DISPLAY ANALYSIS
                    # =========================================

                    st.success(
                        "✅ Article analysed successfully!"
                    )

                    st.subheader(
                        "🧠 Economic Analysis"
                    )

                    st.markdown(analysis)


                    # =========================================
                    # SAVE ANALYSIS
                    # =========================================

                    with st.spinner(
                        "💾 Saving analysis..."
                    ):

                        supabase.table(
                            "articles"
                        ).update(
                            {
                                "analysis": analysis
                            }
                        ).eq(
                            "title",
                            uploaded_file.name
                        ).execute()

                    st.success(
                        "✅ Analysis saved to your article library."
                    )


                except Exception as e:

                    st.error(
                        f"Could not analyse the article: {e}"
                    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AI Article Analyser • Built for daily economic news reading"
)
