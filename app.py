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
    layout="wide"
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
# SIDEBAR
# ============================================================

st.sidebar.title("📰 AI Article Analyser")

page = st.sidebar.radio(
    "Navigate",
    [
        "📰 Analyse Article",
        "📚 My Articles"
    ]
)


# ============================================================
# PAGE 1 — ANALYSE ARTICLE
# ============================================================

if page == "📰 Analyse Article":

    st.title("📰 AI Article Analyser")

    st.markdown(
        "### Turn news into economic understanding."
    )

    st.write(
        "Upload an Economic Times article and understand "
        "the economics behind the news."
    )

    st.divider()

    st.subheader("📄 Upload Article")

    uploaded_file = st.file_uploader(
        "Choose a PDF or TXT article",
        type=["pdf", "txt"]
    )

    if uploaded_file is not None:

        st.success(
            f"Uploaded: {uploaded_file.name}"
        )

        # ====================================================
        # EXTRACT ARTICLE TEXT
        # ====================================================

        extracted_text = ""

        if uploaded_file.name.lower().endswith(".pdf"):

            try:

                pdf_reader = PyPDF2.PdfReader(
                    uploaded_file
                )

                for page in pdf_reader.pages:

                    page_text = page.extract_text()

                    if page_text:

                        extracted_text += (
                            page_text + "\n"
                        )

            except Exception as e:

                st.error(
                    f"Could not read the PDF: {e}"
                )

        else:

            try:

                extracted_text = (
                    uploaded_file
                    .read()
                    .decode(
                        "utf-8",
                        errors="ignore"
                    )
                )

            except Exception as e:

                st.error(
                    f"Could not read the text file: {e}"
                )


        # ====================================================
        # CHECK TEXT
        # ====================================================

        if not extracted_text.strip():

            st.error(
                "I couldn't extract text from this article."
            )

        else:

            # =================================================
            # ARTICLE PREVIEW
            # =================================================

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


            # =================================================
            # ANALYSE BUTTON
            # =================================================

            if st.button(
                "🔍 Analyse Article",
                use_container_width=True
            ):

                # =============================================
                # AI PROMPT
                # =============================================

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


                # =============================================
                # GEMINI ANALYSIS
                # =============================================

                with st.spinner(
                    "🧠 Analysing the article..."
                ):

                    analysis = None
                    last_error = None


                    # -----------------------------------------
                    # FIRST MODEL
                    # -----------------------------------------

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


                    # -----------------------------------------
                    # FALLBACK MODEL
                    # -----------------------------------------

                    if analysis is None:

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


                # =============================================
                # ANALYSIS FAILED
                # =============================================

                if analysis is None:

                    st.error(
                        f"Could not analyse the article: "
                        f"{last_error}"
                    )


                # =============================================
                # ANALYSIS SUCCESSFUL
                # =============================================

                else:

                    st.success(
                        "✅ Article analysed successfully!"
                    )

                    st.subheader(
                        "🧠 Economic Analysis"
                    )

                    st.markdown(
                        analysis
                    )


                    # =========================================
                    # SAVE ARTICLE + ANALYSIS
                    # =========================================

                    st.write(
                        "💾 Saving article..."
                    )

                    article_data = {
                        "title": uploaded_file.name,
                        "source": "Economic Times",
                        "article_text": extracted_text,
                        "analysis": analysis
                    }

                    try:

                        supabase.table(
                            "articles"
                        ).insert(
                            article_data
                        ).execute()

                        st.success(
                            "✅ Article and analysis saved!"
                        )

                    except Exception as e:

                        st.error(
                            f"Could not save the article: {e}"
                        )


# ============================================================
# PAGE 2 — MY ARTICLES
# ============================================================

elif page == "📚 My Articles":

    st.title("📚 My Articles")

    st.write(
        "Your saved economic news and analyses."
    )

    st.divider()


    # ========================================================
    # SEARCH
    # ========================================================

    search_term = st.text_input(
        "🔎 Search your articles",
        placeholder="Search by article title..."
    )


    # ========================================================
    # LOAD ARTICLES
    # ========================================================

    try:

        query = (
            supabase
            .table("articles")
            .select("*")
            .order(
                "created_at",
                desc=True
            )
        )

        if search_term.strip():

            query = query.ilike(
                "title",
                f"%{search_term.strip()}%"
            )

        result = query.execute()

        articles = result.data or []

    except Exception as e:

        st.error(
            f"Could not load your articles: {e}"
        )

        articles = []


    # ========================================================
    # NO ARTICLES
    # ========================================================

    if not articles:

        st.info(
            "No saved articles found."
        )

        st.write(
            "Analyse your first article from "
            "'Analyse Article'."
        )


    # ========================================================
    # ARTICLE LIST
    # ========================================================

    else:

        st.write(
            f"**{len(articles)} article(s) found**"
        )

        for article in articles:

            article_id = article.get("id")

            title = article.get(
                "title",
                "Untitled Article"
            )

            source = article.get(
                "source",
                "Unknown source"
            )

            created_at = article.get(
                "created_at",
                ""
            )


            # =================================================
            # ARTICLE CARD
            # =================================================

            with st.container(border=True):

                st.subheader(
                    title
                )

                st.caption(
                    f"{source} • {created_at}"
                )

                col1, col2 = st.columns(
                    [3, 1]
                )


                # ---------------------------------------------
                # READ
                # ---------------------------------------------

                with col1:

                    if st.button(
                        "📖 Read Article",
                        key=f"read_{article_id}",
                        use_container_width=True
                    ):

                        st.session_state[
                            "selected_article_id"
                        ] = article_id

                        st.session_state.pop(
                            "delete_article_id",
                            None
                        )

                        st.rerun()


                # ---------------------------------------------
                # DELETE
                # ---------------------------------------------

                with col2:

                    if st.button(
                        "🗑️ Delete",
                        key=f"delete_{article_id}",
                        use_container_width=True
                    ):

                        st.session_state[
                            "delete_article_id"
                        ] = article_id

                        st.session_state.pop(
                            "selected_article_id",
                            None
                        )

                        st.rerun()


    # ========================================================
    # DELETE CONFIRMATION
    # ========================================================

    delete_id = st.session_state.get(
        "delete_article_id"
    )

    if delete_id:

        st.divider()

        st.warning(
            "⚠️ Are you sure you want to permanently "
            "delete this article and its analysis?"
        )

        delete_col, cancel_col = st.columns(2)


        # ----------------------------------------------------
        # CONFIRM DELETE
        # ----------------------------------------------------

        with delete_col:

            if st.button(
                "🗑️ Yes, delete permanently",
                key="confirm_delete",
                use_container_width=True
            ):

                try:

                    (
                        supabase
                        .table("articles")
                        .delete()
                        .eq("id", delete_id)
                        .execute()
                    )

                    st.session_state.pop(
                        "delete_article_id",
                        None
                    )

                    st.success(
                        "✅ Article deleted successfully."
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Could not delete article: {e}"
                    )


        # ----------------------------------------------------
        # CANCEL
        # ----------------------------------------------------

        with cancel_col:

            if st.button(
                "Cancel",
                key="cancel_delete",
                use_container_width=True
            ):

                st.session_state.pop(
                    "delete_article_id",
                    None
                )

                st.rerun()


    # ========================================================
    # OPEN SELECTED ARTICLE
    # ========================================================

    selected_id = st.session_state.get(
        "selected_article_id"
    )

    if selected_id:

        st.divider()

        # ----------------------------------------------------
        # GET SELECTED ARTICLE DIRECTLY FROM SUPABASE
        # ----------------------------------------------------

        try:

            selected_result = (
                supabase
                .table("articles")
                .select("*")
                .eq("id", selected_id)
                .execute()
            )

            selected_rows = (
                selected_result.data or []
            )

            if selected_rows:

                selected_article = selected_rows[0]

            else:

                selected_article = None

        except Exception as e:

            selected_article = None

            st.error(
                f"Could not open the article: {e}"
            )


        # ----------------------------------------------------
        # DISPLAY SELECTED ARTICLE
        # ----------------------------------------------------

        if selected_article:

            st.header(
                selected_article.get(
                    "title",
                    "Article"
                )
            )

            st.caption(
                f"{selected_article.get('source', '')} "
                f"• "
                f"{selected_article.get('created_at', '')}"
            )


            # ------------------------------------------------
            # CLOSE
            # ------------------------------------------------

            if st.button(
                "✕ Close Article",
                key="close_article"
            ):

                st.session_state.pop(
                    "selected_article_id",
                    None
                )

                st.rerun()


            st.divider()


            # ------------------------------------------------
            # ORIGINAL ARTICLE
            # ------------------------------------------------

            st.subheader(
                "📄 Original Article"
            )

            st.text_area(
                "Original article",
                selected_article.get(
                    "article_text",
                    ""
                ),
                height=400,
                disabled=True,
                label_visibility="collapsed"
            )


            st.divider()


            # ------------------------------------------------
            # ECONOMIC ANALYSIS
            # ------------------------------------------------

            st.subheader(
                "🧠 Economic Analysis"
            )

            saved_analysis = selected_article.get(
                "analysis",
                ""
            )

            if saved_analysis:

                st.markdown(
                    saved_analysis
                )

            else:

                st.warning(
                    "No analysis is available for this article."
                )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AI Article Analyser • Built for daily economic news reading"
)
