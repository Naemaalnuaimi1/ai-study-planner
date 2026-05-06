import streamlit as st

def apply_phone_style():

    st.markdown("""
    <style>

    /* Hide Streamlit default UI */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Dark background outside phone */
    body {
        background: radial-gradient(circle at center, #0a0f1f 0%, #000 100%);
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Phone container */
    .block-container {
        max-width: 390px !important;
        height: 780px;
        margin: 40px auto !important;
        padding: 25px !important;
        background: #ffffff;
        border-radius: 50px;
        box-shadow: 0 0 80px rgba(0,0,0,0.7);
        overflow-y: auto;
        color: #000000 !important;
    }

    /* Force ALL text black inside phone */
    .block-container h1,
    .block-container h2,
    .block-container h3,
    .block-container h4,
    .block-container p,
    .block-container span,
    .block-container label,
    .block-container div {
        color: #000000 !important;
    }

    /* Notch */
    .notch {
        width: 140px;
        height: 30px;
        background: black;
        border-radius: 20px;
        margin: 10px auto 25px auto;
    }

    /* Textarea */
    textarea {
        border-radius: 18px !important;
        border: 1.5px solid #dcdcdc !important;
        background: #fafafa !important;
        padding: 15px !important;
        color: #000000 !important;
    }

    textarea:focus {
        border: 1.5px solid #007aff !important;
        box-shadow: none !important;
    }

    /* Inputs */
    input {
        border-radius: 16px !important;
        border: 1.5px solid #dcdcdc !important;
        background: #fafafa !important;
        color: #000000 !important;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 22px !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
        border: 1.5px solid #007aff !important;
        background: white !important;
        color: #007aff !important;
    }

    .stButton > button:hover {
        background: #007aff !important;
        color: white !important;
    }

    /* Bottom navigation */
    .bottom-nav {
        position: sticky;
        bottom: 0;
        background: #ffffff;
        border-top: 1px solid #eee;
        padding: 15px 0;
        margin-top: 20px;
    }

    .bottom-nav .stButton > button {
        border-radius: 50% !important;
        width: 55px !important;
        height: 55px !important;
        font-size: 18px !important;
    }

    /* Clean outlined task card */
    .task-card {
        background: #ffffff;
        border-radius: 20px;
        padding: 18px;
        margin-top: 10px;
        border: 2px solid #000000;
    }

    .task-card p {
        margin: 6px 0;
        color: #000000 !important;
        font-size: 15px;
    }

    </style>
    """, unsafe_allow_html=True)
