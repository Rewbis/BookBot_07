"""
Phase 3 View: Scene Drafting.
"""

import streamlit as st
from src.core.graph import create_phase3_graph
from src.core.state import ProjectState
from src.ui.persistence import save_project

def show_phase3():
    st.title("Phase 3: Scene Drafting")
    
    project = st.session_state.project
    
    # Chapter Selection
    chapter_options = [f"Chapter {c.number}: {c.title or 'Untitled'}" for c in project.chapters]
    selected_chapter_idx = st.selectbox("Select Chapter to Draft", range(len(chapter_options)), index=project.current_chapter_index)
    project.current_chapter_index = selected_chapter_idx
    
    chapter = project.chapters[selected_chapter_idx]
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Reference")
        st.write(f"**Outline:**\n{chapter.outline}")
        st.write(f"**Side Notes:**\n{chapter.side_notes}")
        
    with col2:
        st.subheader("Draft")
        if not chapter.draft:
            if st.button(f"🚀 Draft Chapter {chapter.number}"):
                with st.spinner(f"Agents are writing Chapter {chapter.number}..."):
                    graph = create_phase3_graph()
                    initial_state = {
                        "project": project,
                        "critic_feedback": "",
                        "iteration_count": 0
                    }
                    final_state = graph.invoke(initial_state)
                    st.session_state.project = final_state["project"]
                    save_project(st.session_state.project)
                    st.rerun()
        
        if chapter.draft:
            chapter.draft = st.text_area("Prose", value=chapter.draft, height=600, key=f"draft_{selected_chapter_idx}")
            
            if st.button("💾 Save Draft"):
                save_project(project)
                st.success("Draft Saved!")

    st.divider()
    if st.button("⬅️ Back to Outlining"):
        project.current_phase = 2
        st.rerun()

    # Final Export
    if all(c.is_completed for c in project.chapters):
        st.subheader("🎉 Book Complete!")
        if st.button("Export Full Book"):
            full_book = "\n\n".join([f"# {c.title}\n\n{c.draft}" for c in project.chapters])
            st.download_button("Download Book (Markdown)", full_book, file_name="my_book.md")
