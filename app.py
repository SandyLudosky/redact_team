import streamlit as st
import asyncio
from main import run as run_flow

desired_size = (600, 400)

# Streamlit App
st.title("🖼️  Publishing Company ✨")  # Add a title
margin = '<div style="margin: 20px 5px;"></div>'

# User input
with st.form("user_form", clear_on_submit=True):
    user_input = st.text_input("Type something")
    submit_button = st.form_submit_button(label="Send")


if submit_button:
    with st.spinner("Generating ..."):
        result = asyncio.run(run_flow(user_input))  # <-- await the coroutine in sync Streamlit code
        if not result:
            st.warning("No output generated.")
        else:
            summary, image = result
            st.markdown(f"### Summary:\n{summary}")
            st.image(image, caption="Generated Image", use_column_width=True)
# ...existing code...


