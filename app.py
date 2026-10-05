import streamlit as st


def main():
    """Build the Streamlit UI for the home page."""
    st.title("Macro News AI")
    st.write(
        """Welcome to **Macro News AI**! This application will help you develop a daily habit of reading and critically analyzing Economic Times articles for your macroeconomics studies.

In future versions you will be able to:
- Upload an article
- Get a simple explanation of the article
- See the economic context behind the article
- Receive a critical analysis
- Identify relevant macroeconomic concepts
- Suggest related articles
- Check current developments (policy, markets, geopolitics)
- Save your analyses
- Track your daily reading streak
- Get daily reminders
"""
    )

if __name__ == "__main__":
    # Streamlit runs the script top‑to‑bottom, so we call our UI builder.
    main()
