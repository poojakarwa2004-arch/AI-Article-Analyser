import streamlit as st
from google import genai

st.title("🧪 Gemini Model Test")

try:
    gemini = genai.Client(
        api_key=st.secrets["GEMINI_API_KEY"]
    )

    st.success("Gemini API key loaded successfully.")

    models = list(gemini.models.list())

    st.subheader("Models available to this API key")

    for model in models:
        st.write(model.name)

except Exception as e:
    st.error(f"Error: {e}")
