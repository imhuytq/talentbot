"""Main entrypoint for the app."""

import time

import streamlit as st

st.set_page_config(
    page_title="TalentBot - AI-Powered Talent Acquisition Assistant developed by EightyNine team",
    page_icon="🤖",
)
st.header("Welcome!")


def text_generator(text):
    for char in text:
        time.sleep(0.01)
        yield char


# Sử dụng generator
gen = text_generator(
    "Hello, I'm TalentBot, an AI-Powered Talent Acquisition Assistant developed by EightyNine team."
)

st.write_stream(gen)

# open logo.png as bytes
with open("./assets/logo.png", "rb") as f:
    logo = f.read()
    st.image(logo, caption="TalentBot", use_column_width=True)
