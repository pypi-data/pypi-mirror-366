"""Streamlit Home page"""

import streamlit as st
from st_pages import add_indentation

add_indentation()

format_text = """
    <h1 style='text-align: center; margin-top: 0; font-family: sans-serif; font-weight: normal; font-size: 32px;'>
    Welcome To General-purpose Utilities Apps
    </h1>
    <p style='text-align: center; margin-top: 0; font-family: sans-serif; font-weight: normal; font-size: 18px;'>
    Please select the desired utility from the left sidebar
    </p>"""
st.markdown(format_text, unsafe_allow_html=True)
