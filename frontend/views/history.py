import streamlit as st


def render() -> None:
    st.title("📊 Analysis History")
    st.info(
        "Analysis history is unavailable without an account. "
        "Public analyses are not saved to the database."
    )