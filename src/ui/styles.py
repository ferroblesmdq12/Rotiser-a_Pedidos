import streamlit as st

def apply_global_styles():
    st.markdown(
        """
        <style>
        .small-muted { color: #666; font-size: 0.9rem; }
        </style>
        """,
        unsafe_allow_html=True
    )
