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
# SIDEBAR NAVIGATION
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

        # ----------------------------------------------------
        # EXTRACT TEXT
        # ----------------------------------------------------

        extracted_text = ""

        if uploaded_file.name.lower().endswith(".pdf"):

            pdf_reader = PyPDF2.PdfReader(
                uploaded_file
            )

            for page in pdf_reader.pages:

                page_text = page.extract_text()

                if page_text:
                    extracted_text += page_text + "\n"

        else:

            extracted_text = (
                uploaded_file
                .read()
                .decode(
                    "utf-8",
                    errors="ignore"
                )
            )

        # ----------------------------------------------------
        # CHECK TEXT
        # ----------------------------------------------------

        if not extracted_text.strip():

            st.error(
                "I couldn't extract text from this article."
            )

        else:

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

            # ------------------------------------------------
            # ANALYSE
            # ------------------------------------------------

            if st.button(
                "🔍 Analyse Article",
                use_container_width=True
            ):

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

                # --------------------------------------------
                # GEMINI
                # --------------------------------------------

                with st.spinner(
                    "🧠 Analysing the article..."
                ):

                    analysis = None
                    last_error = None

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

                    # ----------------------------------------
                    # FALLBACK MODEL
                    # ----------------------------------------

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

                # --------------------------------------------
                # IF ANALYSIS FAILED
                # --------------------------------------------

                if analysis is None:

                    st.error(
                        f"Could not analyse the article: "
                        f"{last_error}"
                    )

                else:

                    # ----------------------------------------
                    # DISPLAY
                    # ----------------------------------------

                    st.success(
                        "✅ Article analysed successfully!"
                    )

                    st.subheader(
                        "🧠 Economic Analysis"
                    )

                    st.markdown(
                        analysis
                    )

                    # ----------------------------------------
                    # SAVE TO SUPABASE
                    # ----------------------------------------

                    st.write(
                        "💾 Saving article..."
                    )

                    try:

                        article_data = {
                            "title": uploaded_file.name,
                            "source": "Economic Times",
                            "article_text": extracted_text,
                            "analysis": analysis
                        }

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

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    search_term = st.text_input(
        "🔎 Search your articles",
        placeholder="Search by article title..."
    )

    # --------------------------------------------------------
    # FETCH ARTICLES
    # --------------------------------------------------------

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

        articles = result.data

    except Exception as e:

        st.error(
            f"Could not load your articles: {e}"
        )

        articles = []


    # --------------------------------------------------------
    # NO ARTICLES
    # --------------------------------------------------------

    if not articles:

        st.info(
            "No saved articles found."
        )

        st.write(
            "Analyse your first article from the "
            "'Analyse Article' section."
        )


    # --------------------------------------------------------
    # DISPLAY ARTICLES
    # --------------------------------------------------------

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

            # -----------------------------------------------
            # ARTICLE CARD
            # -----------------------------------------------

            with st.container(border=True):

                st.subheader(
                    title
                )

                st.caption(
                    f"{source}  •  {created_at}"
                )

                col1, col2 = st.columns(
                    [3, 1]
                )

                # -------------------------------------------
                # READ
                # -------------------------------------------

                with col1:

                    if st.button(
                        "📖 Read Article",
                        key=f"read_{article_id}",
                        use_container_width=True
                    ):

                        st.session_state[
                            "selected_article"
                        ] = article_id

                # -------------------------------------------
                # DELETE
                # -------------------------------------------

                with col2:

                    if st.button(
                        "🗑️ Delete",
                        key=f"delete_{article_id}",
                        use_container_width=True
                    ):

                        st.session_state[
                            f"confirm_delete_{article_id}"
                        ] = True


                # -------------------------------------------
                # DELETE CONFIRMATION
                # -------------------------------------------

                if st.session_state.get(
                    f"confirm_delete_{article_id}",
                    False
                ):

                    st.warning(
                        "Are you sure you want to permanently "
                        "delete this article and its analysis?"
                    )

                    confirm_col, cancel_col = st.columns(2)

                    with confirm_col:

                        if st.button(
                            "Yes, delete",
                            key=f"confirm_{article_id}",
                            use_container_width=True
                        ):

                            try:

                                supabase.table(
                                    "articles"
                                ).delete().eq(
                                    "id",
                                    article_id
                                ).execute()

                                st.session_state[
                                    f"confirm_delete_{article_id}"
                                ] = False

                                st.session_state.pop(
                                    "selected_article",
                                    None
                                )

                                st.success(
                                    "🗑️ Article deleted."
                                )

                                st.rerun()

                            except Exception as e:

                                st.error(
                                    f"Could not delete article: {e}"
                                )

                    with cancel_col:

                        if st.button(
                            "Cancel",
                            key=f"cancel_{article_id}",
                            use_container_width=True
                        ):

                            st.session_state[
                                f"confirm_delete_{article_id}"
                            ] = False

                            st.rerun()


    # ========================================================
    # SELECTED ARTICLE
    # ========================================================

    selected_id = st.session_state.get(
        "selected_article"
    )

    if selected_id:

        selected_article = next(
            (
                article
                for article in articles
                if article.get("id") == selected_id
            ),
            None
        )

        if selected_article:

            st.divider()

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

            st.subheader(
                "🧠 Economic Analysis"
            )

            st.markdown(
                selected_article.get(
                    "analysis",
                    "No analysis available."
                )
            )
