import streamlit as st
from openai import OpenAI
from app_pages import capture, organize, execute, intro
from utils.style import apply_phone_style


# ---------------------------------
# MUST BE FIRST
# ---------------------------------
st.set_page_config(
    page_title="AI Study Planner",
    page_icon="📚",
    layout="centered"
)

apply_phone_style()

client = OpenAI()


# ---------------------------------
# SESSION STATE
# ---------------------------------
if "screen" not in st.session_state:
    st.session_state.screen = "intro"   # intro -> app

if "intro_step" not in st.session_state:
    st.session_state.intro_step = "splash"

if "page" not in st.session_state:
    st.session_state.page = "Capture"

if "tasks" not in st.session_state:
    st.session_state.tasks = []


# ---------------------------------
# FAKE NOTCH (always visible)
# ---------------------------------
st.markdown('<div class="notch"></div>', unsafe_allow_html=True)


# ---------------------------------
# ROUTING
# ---------------------------------

# ===== INTRO FLOW =====
if st.session_state.screen == "intro":

    intro.show()


# ===== MAIN APP =====
elif st.session_state.screen == "app":

    # Page routing
    if st.session_state.page == "Capture":
        capture.show(client)

    elif st.session_state.page == "Organize":
        organize.show(client)

    elif st.session_state.page == "Execute":
        execute.show()

    # ---------------------------------
    # Bottom Navigation
    # ---------------------------------
    st.markdown('<div class="bottom-nav">', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🧠", key="nav_capture"):
            st.session_state.page = "Capture"
            st.rerun()

    with col2:
        if st.button("📅", key="nav_organize"):
            st.session_state.page = "Organize"
            st.rerun()

    with col3:
        if st.button("🎯", key="nav_execute"):
            st.session_state.page = "Execute"
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
