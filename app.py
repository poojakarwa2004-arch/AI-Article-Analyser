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
# WHAT THE APP DOES
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
        # PDF
        # ----------------------------------------------------

        if uploaded_file.name.lower().endswith(".pdf"):

            pdf_reader = PyPDF2.PdfReader(uploaded_file)

            for page in pdf_reader.pages:

                page_text = page.extract_text()

                if page_text:
                    extracted_text += page_text + "\n"


        # ----------------------------------------------------
        # TXT
        # ----------------------------------------------------

        elif uploaded_file.name.lower().endswith(".txt"):

            extracted_text = uploaded_file.read().decode(
                "utf-8",
                errors="ignore"
            )


        # ----------------------------------------------------
        # CHECK WHETHER TEXT WAS EXTRACTED
        # ----------------------------------------------------

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


            # =================================================
            # SAVE + ANALYSE
            # =================================================

            if st.button(
                "🔍 Analyse Article",
                use_container_width=True
            ):

                try:

                    # ------------------------------------------------
                    # SAVE ARTICLE TO SUPABASE
                    # ------------------------------------------------

                    with st.spinner("💾 Saving article..."):

                        article_data = {
                            "title": uploaded_file.name,
                            "source": "Economic Times",
                            "article_text": extracted_text,
                            "analysis": ""
                        }

                        supabase.table("articles").insert(
                            article_data
                        ).execute()


                    st.success(
                        "✅ Article saved successfully!"
                    )


                    # ------------------------------------------------
                    # AI ANALYSIS
                    # ------------------------------------------------

                    with st.spinner(
                        "🧠 Analysing the article..."
                    ):

                        prompt = f"""
You are an economics tutor helping a first-year MBA student
understand economic news.

Analyse the article clearly, accurately and in a way that
helps the student learn economics rather than merely summarising
the news.

ARTICLE:

{extracted_text}


Your response must contain the following sections:

## 1. ARTICLE SUMMARY

Explain what happened in simple language.

Focus on:
- What happened?
- Who is involved?
- What is changing?
- What are the important numbers or facts?


## 2. WHY IT MATTERS

Explain why this development is economically important.

Connect the news to the broader economy wherever relevant.


## 3. KEY ECONOMIC CONCEPTS

Identify the economic concepts relevant to the article.

For every concept:
- Name the concept
- Explain it simply
- Explain how it appears in this article

Prioritise concepts from:
- Macroeconomics
- Microeconomics
- Inflation
- GDP
- Interest rates
- Monetary policy
- Fiscal policy
- Exchange rates
- Trade
- Employment
- Demand and supply
- Market structures
- Business economics

Only include concepts that are genuinely relevant.


## 4. CAUSE AND EFFECT

Explain the economic chain of events step by step.

Use arrows where helpful.

For example:

Higher oil prices
→ higher input costs
→ higher transportation costs
→ higher prices
→ inflationary pressure


## 5. IMPACT ON THE ECONOMY

Discuss only the areas that are actually relevant:

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

Give 3–5 questions or limitations that an MBA student should think about.

For example:
- What assumptions are being made?
- Who benefits?
- Who loses?
- What information is missing?
- Could there be an alternative explanation?
- What could happen next?


## 7. MBA TAKEAWAY

Give 3–5 concise points that an MBA student should remember
from this article.


IMPORTANT RULES:

1. Do not invent facts.
2. Do not invent statistics.
3. If something is not stated in the article, clearly say that
   it is an interpretation rather than an article fact.
4. Keep the explanation educational and easy to understand.
5. Explain technical economic terminology in simple language.
6. Do not unnecessarily discuss concepts that are unrelated
   to the article.
"""


                        import time

max_attempts = 3
analysis = None

for attempt in range(max_attempts):

    try:

        response = gemini_client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt
        )

        analysis = response.text
        break

    except Exception as e:

        if attempt < max_attempts - 1:

            time.sleep(5)

        else:

            raise e


                    # ------------------------------------------------
                    # DISPLAY ANALYSIS
                    # ------------------------------------------------

                    st.success(
                        "✅ Article analysed successfully!"
                    )

                    st.subheader("🧠 Economic Analysis")

                    st.markdown(analysis)


                    # ------------------------------------------------
                    # SAVE ANALYSIS TO SUPABASE
                    # ------------------------------------------------

                    with st.spinner(
                        "💾 Saving analysis..."
                    ):

                        supabase.table("articles").update(
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


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AI Article Analyser • Built for daily economic news reading"
)
