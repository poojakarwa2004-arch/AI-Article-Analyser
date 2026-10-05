import streamlit as st
import PyPDF2
import time
from supabase import create_client
from google import genai


# -----------------------------
# PAGE CONFIG
# -----------------------------

st.set_page_config(
    page_title="AI Article Analyser",
    page_icon="📰"
)


# -----------------------------
# CONNECTIONS
# -----------------------------

supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

gemini = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)


# -----------------------------
# TITLE
# -----------------------------

st.title("📰 AI Article Analyser")

st.write(
    "### Turn news into economic understanding."
)

st.write(
    "Upload an Economic Times article and understand "
    "its economic concepts, implications and MBA takeaways."
)

st.divider()


# -----------------------------
# UPLOAD
# -----------------------------

uploaded_file = st.file_uploader(
    "Upload an article",
    type=["pdf", "txt"]
)


if uploaded_file is not None:

    st.success(
        f"Uploaded: {uploaded_file.name}"
    )

    # -------------------------
    # EXTRACT TEXT
    # -------------------------

    extracted_text = ""

    if uploaded_file.name.lower().endswith(".pdf"):

        pdf_reader = PyPDF2.PdfReader(uploaded_file)

        for page in pdf_reader.pages:

            text = page.extract_text()

            if text:
                extracted_text += text + "\n"

    else:

        extracted_text = uploaded_file.read().decode(
            "utf-8",
            errors="ignore"
        )


    # -------------------------
    # CHECK TEXT
    # -------------------------

    if not extracted_text.strip():

        st.error(
            "I couldn't extract text from this file."
        )

    else:

        # ---------------------
        # PREVIEW
        # ---------------------

        with st.expander("📖 View extracted article"):

            st.text_area(
                "Article",
                extracted_text,
                height=400,
                label_visibility="collapsed"
            )


        st.divider()


        # ---------------------
        # ANALYSE BUTTON
        # ---------------------

        if st.button(
            "🔍 Analyse Article",
            use_container_width=True
        ):

            # =================
            # SAVE ARTICLE
            # =================

            st.write("💾 Saving article...")

            article_data = {
                "title": uploaded_file.name,
                "source": "Economic Times",
                "article_text": extracted_text,
                "analysis": ""
            }

            try:

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


            # =================
            # AI PROMPT
            # =================

            prompt = f"""
You are an economics tutor helping a first-year MBA student.

Analyse the following economic news article.

ARTICLE:

{extracted_text}

Give the analysis in these sections:

## 1. ARTICLE SUMMARY

Explain what happened in simple language.

## 2. WHY IT MATTERS

Explain why this development is economically important.

## 3. KEY ECONOMIC CONCEPTS

Identify the economic concepts relevant to the article.

For each concept:
- Name it
- Explain it simply
- Explain how it applies to this article

Only include genuinely relevant concepts.

## 4. CAUSE AND EFFECT

Explain the economic chain step by step.

Use arrows where useful.

## 5. ECONOMIC IMPACT

Discuss relevant effects on:
- Inflation
- GDP / growth
- Employment
- Interest rates
- Government finances
- Businesses
- Consumers
- Investment
- Trade
- Exchange rates

Only discuss areas that are actually relevant.

## 6. CRITICAL THINKING

Give 3–5 questions or limitations an MBA student should consider.

## 7. MBA TAKEAWAY

Give 3–5 things an MBA student should remember.

IMPORTANT:
- Do not invent facts.
- Do not invent statistics.
- Clearly distinguish article facts from interpretation.
- Explain technical economic terms simply.
- Do not discuss unrelated concepts.
"""


            # =================
            # GEMINI ANALYSIS
            # =================

            st.write(
                "🧠 Analysing the article..."
            )

            analysis = None
            error_message = None


            for attempt in range(3):

                try:

                    response = gemini.models.generate_content(
                        model="gemini-3.8-flash",
                        contents=prompt
                    )

                    analysis = response.text
                    break

                except Exception as e:

                    error_message = str(e)

                    if attempt < 2:

                        time.sleep(5)


            # =================
            # HANDLE FAILURE
            # =================

            if analysis is None:

                st.error(
                    f"Could not analyse the article: {error_message}"
                )

            else:

                # =================
                # DISPLAY ANALYSIS
                # =================

                st.success(
                    "✅ Article analysed successfully!"
                )

                st.subheader(
                    "🧠 Economic Analysis"
                )

                st.markdown(analysis)


                # =================
                # SAVE ANALYSIS
                # =================

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

                    st.error(
                        f"Analysis was generated, but could not be saved: {e}"
                    )


# -----------------------------
# FOOTER
# -----------------------------

st.divider()

st.caption(
    "AI Article Analyser • Built for daily economic news reading"
)
