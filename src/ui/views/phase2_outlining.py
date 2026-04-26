"""
Phase 2 View: Chapter Outlining.
"""

import streamlit as st
from src.core.graph import create_phase2_graph
from src.core.state import ProjectState, Chapter
from src.core.agents.phase2 import Phase2SceneWriter
from src.ui.persistence import save_project

def show_phase2():
    st.title("Phase 2: Chapter Outlining")
    
    project = st.session_state.project
    
    if not project.chapters or not project.chapters[0].outline:
        st.info("No outlines generated yet. Let the agents create them based on your plan.")
        if st.button("🚀 Generate Chapter Outlines", help="Asks the agents to create detailed outlines for every chapter based on your book plan and characters."):
            with st.status("Agents are outlining the chapters...", expanded=True) as status:
                st.write("✒️ Scene Writer is drafting detailed chapter outlines...1/4")
                graph = create_phase2_graph()
                initial_state = {
                    "project": project,
                    "critic_feedback": "",
                    "iteration_count": 0
                }
                
                final_state = None
                for event in graph.stream(initial_state):
                    if "writer" in event:
                        st.write("🔍 Continuity Checker is verifying narrative flow...2/4")
                        final_state = event["writer"]
                    elif "checker" in event:
                        st.write("🔄 Refining outlines based on continuity check...3/4")
                        final_state = event["checker"]
                
                if final_state:
                    st.session_state.project = final_state["project"]
                
                status.update(label="Outlining Complete! 4/4", state="complete", expanded=False)
                save_project(st.session_state.project)
                st.rerun()

    if project.chapters and project.chapters[0].outline:
        st.subheader("Edit Chapter Outlines")
        
        for i, chapter in enumerate(project.chapters):
            with st.expander(f"Chapter {chapter.number}: {chapter.title or 'Untitled'}"):
                # Use local variables for UI state to avoid direct mutation
                new_title = st.text_input("Title", value=chapter.title, key=f"ch_title_{i}")
                new_wc = st.number_input("Target Wordcount", value=chapter.rough_wordcount, key=f"ch_wc_{i}")
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    new_outline = st.text_area("Outline", value=chapter.outline, height=200, key=f"ch_outline_{i}")
                with col2:
                    new_notes = st.text_area("Side Notes (Characters/Locations)", value=chapter.side_notes, height=200, key=f"ch_notes_{i}")

                btn_col1, btn_col2, _ = st.columns([1, 2, 2])
                with btn_col1:
                    if st.button("💾 Save Chapter", key=f"save_ch_{i}"):
                        # Apply changes to the model only on save
                        chapter.title = new_title
                        chapter.rough_wordcount = new_wc
                        chapter.outline = new_outline
                        chapter.side_notes = new_notes
                        save_project(st.session_state.project)
                        st.toast(f"Chapter {chapter.number} saved!")
                
                with btn_col2:
                    if st.button("🔄 Re-generate Subsequent", key=f"regen_ch_{i}", help="WARNING: This will overwrite ALL chapters following this one."):
                        # Apply current edits first so the model sees them as the "fixed" context
                        chapter.title = new_title
                        chapter.rough_wordcount = new_wc
                        chapter.outline = new_outline
                        chapter.side_notes = new_notes
                        save_project(project)
                        
                        with st.status(f"Re-generating chapters from {chapter.number + 1} onwards...") as status:
                            writer = Phase2SceneWriter()
                            new_outlines = writer.regenerate_subsequent_chapters(project, i)
                            if new_outlines:
                                fixed_chapters = project.chapters[:i+1]
                                updated_chapters = []
                                for j, r in enumerate(new_outlines):
                                    # Ensure numbering is correct
                                    r["number"] = i + 2 + j
                                    updated_chapters.append(Chapter(**r))
                                
                                project.chapters = fixed_chapters + updated_chapters
                                st.session_state.project = project
                                save_project(project)
                                status.update(label="Re-generation complete!", state="complete")
                                st.rerun()
                            else:
                                status.update(label="No subsequent chapters to generate.", state="error")

        st.divider()
        if st.button("✅ Confirm Outlines & Move to Drafting", help="Finalizes the outlines and unlocks the scene drafting phase."):
            project.current_phase = 3
            st.rerun()
        
        if st.button("⬅️ Back to Planning", help="Returns to Phase 1 to edit the core plan or characters."):
            project.current_phase = 1
            st.rerun()
