"""
Phase 2 View: Chapter Outlining.
"""

import streamlit as st
from src.core.graph import create_phase2_graph
from src.core.state import ProjectState

def show_phase2():
    st.title("Phase 2: Chapter Outlining")
    
    project = st.session_state.project
    
    if not project.chapters or not project.chapters[0].outline:
        st.info("No outlines generated yet. Let the agents create them based on your plan.")
        if st.button("🚀 Generate Chapter Outlines"):
            with st.spinner("Agents are outlining the chapters..."):
                graph = create_phase2_graph()
                initial_state = {
                    "project": project,
                    "critic_feedback": "",
                    "iteration_count": 0
                }
                final_state = graph.invoke(initial_state)
                st.session_state.project = final_state["project"]
                st.rerun()

    if project.chapters and project.chapters[0].outline:
        st.subheader("Edit Chapter Outlines")
        
        for i, chapter in enumerate(project.chapters):
            with st.expander(f"Chapter {chapter.number}: {chapter.title or 'Untitled'}"):
                chapter.title = st.text_input("Title", value=chapter.title, key=f"ch_title_{i}")
                chapter.rough_wordcount = st.number_input("Target Wordcount", value=chapter.rough_wordcount, key=f"ch_wc_{i}")
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    chapter.outline = st.text_area("Outline", value=chapter.outline, height=200, key=f"ch_outline_{i}")
                with col2:
                    chapter.side_notes = st.text_area("Side Notes (Characters/Locations)", value=chapter.side_notes, height=200, key=f"ch_notes_{i}")

        st.divider()
        if st.button("✅ Confirm Outlines & Move to Drafting"):
            project.current_phase = 3
            st.rerun()
        
        if st.button("⬅️ Back to Planning"):
            project.current_phase = 1
            st.rerun()
