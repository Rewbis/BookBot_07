"""
Main Streamlit Application for BookBot_07.
"""

import streamlit as st
import os
from src.core.state import ProjectState
from src.ui.persistence import save_project, load_project
from src.ui.views.phase1_planning import show_phase1
from src.ui.views.phase2_outlining import show_phase2
from src.ui.views.phase3_drafting import show_phase3

# Page Configuration
st.set_page_config(
    page_title="BookBot 07 - Agentic Narrative Engine",
    page_icon="src/assets/bookbot.ico",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #2e3136;
        color: white;
    }
    .stButton>button:hover {
        background-color: #4e5156;
        border-color: #00ff00;
    }
    </style>
    """, unsafe_allow_html=True)

# Session State Initialization
if "project" not in st.session_state:
    st.session_state.project = load_project()

def main():
    st.sidebar.title("🤖 BookBot 07")
    
    # Navigation
    phase = st.sidebar.radio(
        "Navigation",
        ["Phase 1: Planning", "Phase 2: Outlining", "Phase 3: Drafting"],
        index=st.session_state.project.current_phase - 1
    )
    
    # Save button in sidebar
    if st.sidebar.button("💾 Save Project"):
        save_project(st.session_state.project)
        st.sidebar.success("Project Saved!")

    # Update phase in project state
    if phase == "Phase 1: Planning":
        st.session_state.project.current_phase = 1
        show_phase1()
    elif phase == "Phase 2: Outlining":
        st.session_state.project.current_phase = 2
        show_phase2()
    elif phase == "Phase 3: Drafting":
        st.session_state.project.current_phase = 3
        show_phase3()

if __name__ == "__main__":
    main()
