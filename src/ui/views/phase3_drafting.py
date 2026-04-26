"""
Phase 3 View: Scene Drafting.
"""

import streamlit as st
from src.core.graph import create_phase3_graph
from src.core.state import ProjectState
from src.ui.persistence import save_project
from src.core.utils import parse_range_string

def show_phase3():
    st.title("Phase 3: Scene Drafting")
    
    project = st.session_state.project
    
    # Bulk Drafting Section
    with st.expander("🚀 Bulk Drafting"):
        col_range, col_btn = st.columns([3, 1])
        range_input = col_range.text_input("Enter chapters (e.g., 1-5, 8, 10-12)", help="Specify chapter numbers or ranges to draft in bulk.")
        if col_btn.button("Draft All"):
            chapter_nums = parse_range_string(range_input, len(project.chapters))
            if not chapter_nums:
                st.error("Invalid range or no chapters found.")
            else:
                graph = create_phase3_graph()
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, ch_num in enumerate(chapter_nums):
                    ch_idx = ch_num - 1
                    current_ch = project.chapters[ch_idx]
                    status_text.write(f"📝 **Bulk Progress:** Drafting Chapter {ch_num} ({i+1}/{len(chapter_nums)})...")
                    
                    initial_state = {
                        "project": project,
                        "critic_feedback": "",
                        "iteration_count": 0
                    }
                    project.current_chapter_index = ch_idx
                    
                    # Run graph for this chapter
                    for event in graph.stream(initial_state):
                        if "editor" in event:
                            project = event["editor"]["project"]
                    
                    progress_bar.progress((i + 1) / len(chapter_nums))
                    save_project(project)
                
                st.success(f"Successfully drafted {len(chapter_nums)} chapters!")
                st.rerun()
    
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
            if st.button(f"🚀 Draft Chapter {chapter.number}", help="Starts the 4-agent drafting pipeline (Action → Sensory → Voice → Editor). This usually takes 1-2 minutes per chapter."):
                graph = create_phase3_graph()
                initial_state = {
                    "project": project,
                    "critic_feedback": "",
                    "iteration_count": 0
                }
                
                with st.status(f"Writing Chapter {chapter.number}...", expanded=True) as status:
                    st.write("🎬 Action Agent is setting the scene...1/5")
                    for event in graph.stream(initial_state):
                        if "action" in event:
                            st.write("👃 Sensory Agent is adding details...2/5")
                            project = event["action"]["project"]
                        elif "sensory" in event:
                            st.write("🗣️ Voice Agent is styling prose...3/5")
                            project = event["sensory"]["project"]
                        elif "voice" in event:
                            st.write("✍️ Editor Agent is polishing...4/5")
                            project = event["voice"]["project"]
                        elif "editor" in event:
                            project = event["editor"]["project"]
                    
                    status.update(label="Drafting Complete! 5/5", state="complete", expanded=False)
                
                st.session_state.project = project
                save_project(st.session_state.project)
                st.rerun()
        
        if chapter.draft:
            chapter.draft = st.text_area("Prose", value=chapter.draft, height=600, key=f"draft_{selected_chapter_idx}")
            
            if st.button("💾 Save Draft", help="Saves the current edits to this chapter's prose."):
                save_project(project)
                st.success("Draft Saved!")

    st.divider()
    if st.button("⬅️ Back to Outlining", help="Returns to Phase 2 to refine the chapter outlines."):
        project.current_phase = 2
        st.rerun()

    # Final Export
    if all(c.is_completed for c in project.chapters):
        st.subheader("🎉 Book Complete!")
        if st.button("Export Full Book", help="Combines all drafted chapters into a single Markdown file for download."):
            full_book = "\n\n".join([f"# {c.title}\n\n{c.draft}" for c in project.chapters])
            st.download_button("Download Book (Markdown)", full_book, file_name="my_book.md")
