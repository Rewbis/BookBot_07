"""
Phase 1 View: Planning and Brainstorming.
"""

import streamlit as st
from src.core.graph import create_phase1_graph, GraphState
from src.core.state import ProjectState, Character, Location, Event, Chapter
from src.ui.persistence import save_project
from src.core.agents.phase1 import Phase1Plotter

def show_phase1():
    st.title("Phase 1: Planning & Brainstorming")
    
    project = st.session_state.project
    
    # Idea Input
    with st.expander("Step 1: Your Book Idea", expanded=not bool(project.book_idea)):
        idea = st.text_area("What's the core concept of your book?", value=project.book_idea, help="Provide a few sentences or a paragraph describing your story idea.")
        if st.button("Generate Initial Plan", help="Invokes agents to brainstorm a full narrative plan and key world elements based on your idea.") and idea:
            project.book_idea = idea
            with st.status("Agents are brainstorming...", expanded=True) as status:
                st.write("📝 Plotter is drafting the narrative plan and world elements... 1/4")
                graph = create_phase1_graph()
                initial_state = {
                    "project": project,
                    "critic_feedback": "",
                    "iteration_count": 0
                }
                
                final_state = None
                for event in graph.stream(initial_state):
                    if "plotter" in event:
                        st.write("⚖️ Critic is reviewing the plan for weaknesses...2/4")
                        final_state = event["plotter"]
                    elif "critic" in event:
                        # Iteration count check happens in graph, we just report progress
                        st.write("🔄 Refining plan based on critique...3/4")
                        final_state = event["critic"]
                
                if final_state:
                    st.session_state.project = final_state["project"]
                
                status.update(label="Brainstorming Complete! 4/4", state="complete", expanded=False)
                save_project(st.session_state.project)
                st.rerun()

    if project.book_plan:
        st.divider()
        
        # Plan Editing
        st.subheader("Step 2: Refine the Plan")
        new_plan = st.text_area("Narrative Plan", value=project.book_plan, height=300)
        
        col1, col2 = st.columns(2)
        with col1:
            new_target_chapters = st.number_input("Target Chapters", value=project.target_chapters, min_value=1)
        with col2:
            new_target_wordcount = st.number_input("Target Wordcount", value=project.target_total_wordcount, min_value=1000)

        # Style Profile
        st.subheader("Step 3: Style Profile")
        with st.expander("Define the Book's Voice", expanded=True):
            new_tone = st.text_input("Tone (e.g., dark and lyrical)", value=project.style_profile.tone, help="Describes the atmosphere and mood of the prose.")
            new_pov = st.text_input("POV (e.g., third person limited)", value=project.style_profile.pov, help="Point of view the book will be written in.")
            new_sample = st.text_area("Sample Prose (for style matching)", value=project.style_profile.sample_prose, height=150, help="Paste ~200 words of writing you admire to help the agents mimic the style.")

        # Data Elements Tabs (World Bible)
        st.subheader("Step 4: World Bible")
        tab1, tab2, tab3 = st.tabs(["Characters", "Locations", "Events"])
        
        with tab1:
            st.write("### Characters")
            for i, char in enumerate(project.characters):
                with st.expander(f"Character: {char.name}"):
                    char.name = st.text_input(f"Name", value=char.name, key=f"char_name_{i}")
                    char.role = st.text_input(f"Role", value=char.role, key=f"char_role_{i}")
                    char.description = st.text_area(f"Description", value=char.description, key=f"char_desc_{i}")
            
            if st.button("Add Character"):
                project.characters.append(Character(name="New Character", role="Side Character", description=""))
                save_project(project)
                st.rerun()

        with tab2:
            st.write("### Locations")
            for i, loc in enumerate(project.locations):
                with st.expander(f"Location: {loc.name}"):
                    loc.name = st.text_input(f"Name", value=loc.name, key=f"loc_name_{i}")
                    loc.description = st.text_area(f"Description", value=loc.description, key=f"loc_desc_{i}")
            
            if st.button("Add Location"):
                project.locations.append(Location(name="New Location", description=""))
                save_project(project)
                st.rerun()

        with tab3:
            st.write("### Events")
            for i, ev in enumerate(project.events):
                with st.expander(f"Event: {ev.title}"):
                    ev.title = st.text_input(f"Title", value=ev.title, key=f"ev_title_{i}")
                    ev.description = st.text_area(f"Description", value=ev.description, key=f"ev_desc_{i}")
            
            if st.button("Add Event"):
                project.events.append(Event(title="New Event", description=""))
                save_project(project)
                st.rerun()

        # Save and Progression
        st.divider()
        col_save, col_move = st.columns([1, 1])
        
        with col_save:
            if st.button("💾 Save All Changes", help="Persists all edits to the narrative plan, style, and world bible."):
                project.book_plan = new_plan
                project.target_chapters = new_target_chapters
                project.target_total_wordcount = new_target_wordcount
                project.style_profile.tone = new_tone
                project.style_profile.pov = new_pov
                project.style_profile.sample_prose = new_sample
                # Note: Character/Location/Event names are already updated via their keys in the loop
                save_project(project)
                st.success("Project Saved!")

        with col_move:
            if st.button("✅ Confirm Plan & Move to Outlining", help="Finalizes this phase and prepares the project for detailed chapter-by-chapter outlining."):
                # Apply latest edits before moving
                project.book_plan = new_plan
                project.target_chapters = new_target_chapters
                project.target_total_wordcount = new_target_wordcount
                project.style_profile.tone = new_tone
                project.style_profile.pov = new_pov
                project.style_profile.sample_prose = new_sample
                
                # Initialize chapters if they don't exist
                if not project.chapters or len(project.chapters) != project.target_chapters:
                    project.chapters = [Chapter(number=i+1) for i in range(project.target_chapters)]
                
                # Extract premise for drafting context
                if not project.premise:
                    plotter = Phase1Plotter()
                    project.premise = plotter.generate_premise(project.book_plan)
                
                project.current_phase = 2
                save_project(project)
                st.rerun()
