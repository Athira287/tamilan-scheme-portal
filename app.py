import streamlit as st
import pandas as pd
import hashlib
import base64
import re
import os

# 1. Page Config
st.set_page_config(page_title="Tamilan Scheme Portal", layout="wide")

# 2. Hide Headers
st.markdown(
    """
    <style>
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

# 3. Session State
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# 4. Login Function
def login_page():
    st.title("🔒 Tamilan Scheme Portal - Login")
    username = st.text_input("Username / Aadhaar ID")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if username == "admin" and password == "sih2026":
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Invalid Username or Password")

# 5. App Flow
if not st.session_state["authenticated"]:
    login_page()
else:
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"authenticated": False}))
    
    # ----------------------------------------------------
    # UNGA PAZHAYA DASHBOARD CODE INGA VARANUM
    # ----------------------------------------------------
    st.title("Notifications & Status Dashboard")
    st.info("📌 Security Alert: Document vault encryption state is ACTIVE.")
