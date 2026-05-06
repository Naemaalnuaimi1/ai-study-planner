import streamlit as st
import time


def show():

    # -------------------------
    # Initialize intro state
    # -------------------------
    if "intro_step" not in st.session_state:
        st.session_state.intro_step = "splash"

    # -------------------------
    # SPLASH SCREEN
    # -------------------------
    if st.session_state.intro_step == "splash":

        st.markdown("<div class='notch'></div>", unsafe_allow_html=True)

        st.markdown("""
            <div style='text-align:center; margin-top:120px;'>
                <h1 style='font-size:38px;'>📚</h1>
                <h2 style='margin-top:10px;'>AI Study Planner</h2>
                <p style='color:gray;'>Organize. Focus. Execute.</p>
            </div>
        """, unsafe_allow_html=True)

        time.sleep(1.5)

        st.session_state.intro_step = "login"
        st.rerun()

    # -------------------------
    # LOGIN SCREEN
    # -------------------------
    elif st.session_state.intro_step == "login":

        st.markdown("<div class='notch'></div>", unsafe_allow_html=True)

        st.markdown("""
            <div style='text-align:center; margin-top:60px;'>
                <h2>Welcome Back 👋</h2>
            </div>
        """, unsafe_allow_html=True)

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("Login"):

            # 🔐 Simple prototype login (no real auth yet)
            if username and password:
                st.session_state.screen = "app"
                st.rerun()
            else:
                st.warning("Please enter username and password.")
