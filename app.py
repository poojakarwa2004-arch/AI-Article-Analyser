import streamlit as st
import PyPDF2
import time
from supabase import create_client
from google import genai


# ============================================================
# PAGE CONFIG
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

gemini = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)


# ============================================================
# TITLE
# ============================================================

st.title("📰 AI Article Analyser")

st.markdown(
    "### Turn news into economic understanding."
)

st.write(
    "Upload an Economic Times article and understand "
    "the economics behind the news."
)

st.divider()


# ============================================================
# UPLOAD ARTICLE
# ============================================================

st.subheader("📄 Upload Article")

uploaded_file = st.file_uploader(
    "Choose a PDF or TXT article",
    type=["pdf", "txt"]
)


if uploaded_file is not None:

    st.success(
        f"Uploaded: {uploaded_file.name}"
    )


    # ========================================================
    # EXTRACT TEXT
    # ========================================================

    extracted_text = ""


    if uploaded_file.name.lower().endswith(".pdf"):

        pdf_reader = PyPDF2.PdfReader(
            uploaded_file
        )

        for page in pdf_reader.pages:

            page_text = page.extract_text()

            if page_text:

                extracted_text += (
                    page_text + "\n"
                )


    else:

        extracted_text = (
            uploaded_file
            .read()
            .decode(
                "utf-8",
                errors="ignore"
            )
        )


    # ========================================================
    # CHECK ARTICLE
    # ========================================================

    if not extracted_text.strip():

        st.error(
            "I couldn't extract text from this article."
        )

    else:

        # ====================================================
        # ARTICLE PREVIEW
        # ====================================================

        with st.expander(
            "📖 View extracted article"
        ):

            st.text_area(
                "Article text",
                extracted_text,
                height=400,
                label_visibility="collapsed"
            )


        st.divider()


        # ====================================================
        # ANALYSE
        # ====================================================

        if st.button(
            "🔍 Analyse Article",
            use_container_width=True
        ):

            # =================================================
            # SAVE ARTICLE
            # =================================================

            try:

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

            except Exception as e:

                st.error(
                    f"Could not save the article: {e}"
                )


            # =================================================
            # PROMPT
            # =================================================

            prompt = f"""
You are an economics tutor helping a first-year MBA student.

Analyse the following economic news article.

ARTICLE:

{extracted_text}


Give your response using these sections:


## 1. ARTICLE SUMMARY

Explain what happened in simple language.

Include:
- What happened?
- Who is involved?
- What is changing?
- Important numbers or facts.


## 2. WHY IT MATTERS

Explain why this development is economically important.

Connect it to the broader economy where relevant.


## 3. KEY ECONOMIC CONCEPTS

Identify the economic concepts relevant to this article.

For every concept:

- Name the concept
- Explain it simply
- Explain how it applies to the article

Only include concepts that are genuinely relevant.


## 4. CAUSE AND EFFECT

Explain the economic chain step by step.

Use arrows where useful.

Example:

Higher oil prices
→ higher input costs
→ higher transportation costs
→ higher prices
→ inflationary pressure


## 5. ECONOMIC IMPACT

Discuss only the relevant effects on:

- Inflation
- GDP / economic growth
- Employment
- Interest rates
- Government finances
- Businesses
- Consumers
- Investment
- Trade
- Exchange rates


## 6. CRITICAL THINKING

Give 3–5 questions or limitations an MBA student
should consider.

Think about:

- assumptions
- winners and losers
- missing information
- alternative explanations
- what could happen next


## 7. MBA TAKEAWAY

Give 3–5 concise points an MBA student should remember.


IMPORTANT RULES:

1. Do not invent facts.
2. Do not invent statistics.
3. Clearly distinguish article facts from interpretation.
4. Explain technical economic terminology simply.
5. Do not discuss unrelated concepts.
"""


            # =================================================
            # GEMINI ANALYSIS
            # =================================================

            st.write(
                "🧠 Analysing the article..."
            )

            analysis = None
            last_error = None


            # =================================================
            # TRY LIGHTWEIGHT MODEL
            # =================================================

            for attempt in range(2):

                try:

                    response = (
                        gemini.models.generate_content(
                            model="gemini-3.1-flash-lite",
                            contents=prompt
                        )
                    )

                    analysis = response.text

                    break

                except Exception as e:

                    last_error = e

                    if attempt == 0:

                        time.sleep(5)


            # =================================================
            # FALLBACK MODEL
            # =================================================

            if analysis is None:

                st.write(
                    "Trying the backup Gemini model..."
                )

                try:

                    response = (
                        gemini.models.generate_content(
                            model="gemini-3.6-flash",
                            contents=prompt
                        )
                    )

                    analysis = response.text

                except Exception as e:

                    last_error = e


            # =================================================
            # RESULT
            # =================================================

            if analysis is None:

                st.error(
                    f"Could not analyse the article: {last_error}"
                )

            else:

                # =============================================
                # DISPLAY
                # =============================================

                st.success(
                    "✅ Article analysed successfully!"
                )

                st.subheader(
                    "🧠 Economic Analysis"
                )

                st.markdown(
                    analysis
                )


                # =============================================
                # SAVE ANALYSIS
                # =============================================

                try:

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
                        "💾 Analysis saved to your article library."
                    )

                except Exception as e:

                    st.warning(
                        "The analysis was generated, "
                        "but could not be saved to Supabase."
                    )

                    st.caption(
                        str(e)
                    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AI Article Analyser • Built for daily economic news reading"
)
