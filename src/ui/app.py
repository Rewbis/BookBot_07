"""
Main Streamlit Application for BookBot_07.
"""
import os
os.environ["TRANSFORMERS_VERBOSITY"] = "error"

import streamlit as st
from src.core.state import ProjectState
from src.ui.persistence import save_project, load_project
# View imports deferred to improve startup time.

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

if "telemetry" not in st.session_state:
    st.session_state.telemetry = {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0
    }

def main():
    st.sidebar.title("🤖 BookBot 07")
    
    # Navigation
    phase = st.sidebar.radio(
        "Navigation",
        ["Phase 1: Planning", "Phase 2: Outlining", "Phase 3: Drafting", "Phase 4: Marketing & Artwork", "Phase 5: Publishing"],
        index=min(st.session_state.project.current_phase - 1, 4)
    )
    
    # Save/Load Section
    st.sidebar.divider()
    st.sidebar.subheader("Project Management")
    
    # Save as Version (Timestamped)
    if st.sidebar.button("📦 Save as Version", help="Creates a new timestamped file (e.g., MyBook_2024.json). Perfect for backups and versioning."):
        fname = save_project(st.session_state.project, use_timestamp=True)
        st.sidebar.success(f"Saved: {fname}")

    # Standard Save
    if st.sidebar.button("💾 Save Project", help="Overwrites the main project_state.json file. Use this for quick, frequent saves."):
        save_project(st.session_state.project)
        st.sidebar.success("Project Saved!")
        
    # Load Project
    uploaded_file = st.sidebar.file_uploader("📂 Load Project JSON", type=["json"])
    if uploaded_file is not None:
        try:
            import json
            data = json.load(uploaded_file)
            st.session_state.project = ProjectState(**data)
            st.sidebar.success("Project Loaded!")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Error loading file: {e}")

    # Telemetry Section
    st.sidebar.divider()
    st.sidebar.subheader("📊 Model Telemetry")
    t = st.session_state.telemetry
    st.sidebar.metric("Prompt Tokens", f"{t['prompt_tokens']:,}")
    st.sidebar.metric("Completion Tokens", f"{t['completion_tokens']:,}")
    st.sidebar.metric("Total Tokens", f"{t['total_tokens']:,}")

    # New Project
    st.sidebar.divider()
    if st.sidebar.button("✨ New Project", help="Wipes current state and starts fresh"):
        st.session_state.confirm_new = True
        
    if st.session_state.get("confirm_new"):
        st.sidebar.warning("Are you sure? All unsaved progress will be lost.")
        col1, col2 = st.sidebar.columns(2)
        if col1.button("✅ Yes, Reset", type="primary"):
            st.session_state.project = ProjectState()
            save_project(st.session_state.project)
            st.session_state.confirm_new = False
            st.rerun()
        if col2.button("❌ Cancel"):
            st.session_state.confirm_new = False
            st.rerun()

    # Update phase in project state
    if phase == "Phase 1: Planning":
        from src.ui.views.phase1_planning import show_phase1
        st.session_state.project.current_phase = 1
        show_phase1()
    elif phase == "Phase 2: Outlining":
        from src.ui.views.phase2_outlining import show_phase2
        st.session_state.project.current_phase = 2
        show_phase2()
    elif phase == "Phase 3: Drafting":
        from src.ui.views.phase3_drafting import show_phase3
        st.session_state.project.current_phase = 3
        show_phase3()
    elif phase == "Phase 4: Marketing & Artwork":
        from src.ui.views.phase4_publishing import show_phase4
        st.session_state.project.current_phase = 4
        show_phase4()
    elif phase == "Phase 5: Publishing":
        from src.ui.views.phase5_publishing import show_phase5
        st.session_state.project.current_phase = 5
        show_phase5()

if __name__ == "__main__":
    main()
