import streamlit as st
from src.core.agents.phase4 import Phase4MarketingAgent, Phase4ImageAgent
from src.ui.persistence import save_project

def show_phase4():
    st.header("Phase 4: Publishing & Marketing")
    st.markdown("Generate marketing copy, back-cover blurbs, and image prompts for your book.")
    
    project = st.session_state.project
    marketing_agent = Phase4MarketingAgent()
    image_agent = Phase4ImageAgent()
    
    tab1, tab2 = st.tabs(["Marketing Copy", "Artwork Prompts"])
    
    # --- TAB 1: Marketing Copy ---
    with tab1:
        st.subheader("Back-Cover Blurb")
        if st.button("Generate Blurb", help="Generates a punchy 150-200 word blurb based on your premise and characters."):
            with st.spinner("Writing blurb..."):
                project.blurb = marketing_agent.generate_blurb(project)
                save_project(project)
                st.rerun()
                
        blurb_val = st.text_area("Blurb", value=project.blurb, height=200, label_visibility="collapsed")
        if blurb_val != project.blurb:
            project.blurb = blurb_val
            save_project(project)
            
        st.divider()
        
        st.subheader("Amazon / Kindle Copy")
        if st.button("Generate Kindle Copy", help="Generates structured sales copy with hooks and bullet points."):
            with st.spinner("Writing marketing copy..."):
                project.marketing_copy = marketing_agent.generate_marketing_copy(project)
                save_project(project)
                st.rerun()
                
        marketing_val = st.text_area("Marketing Copy", value=project.marketing_copy, height=300, label_visibility="collapsed")
        if marketing_val != project.marketing_copy:
            project.marketing_copy = marketing_val
            save_project(project)
            
    # --- TAB 2: Artwork Prompts ---
    with tab2:
        st.subheader("Base Visual Style")
        st.markdown("This style string is appended to all image prompts to maintain a consistent aesthetic.")
        
        if st.button("Derive Style from Project", help="Suggests a base style based on your Tone and Sample Prose."):
            with st.spinner("Deriving style..."):
                project.style_profile.image_style = image_agent.derive_image_style(project)
                save_project(project)
                st.rerun()
                
        style_val = st.text_input("Visual Style", value=project.style_profile.image_style, label_visibility="collapsed", placeholder="e.g., cinematic lighting, dark fantasy, watercolor")
        if style_val != project.style_profile.image_style:
            project.style_profile.image_style = style_val
            save_project(project)
            
        st.divider()
        
        st.subheader("Book Cover")
        if st.button("Generate Cover Prompt"):
            with st.spinner("Generating cover prompt..."):
                project.cover_prompt = image_agent.generate_cover_prompt(project)
                save_project(project)
                st.rerun()
                
        cover_val = st.text_area("Cover Prompt", value=project.cover_prompt, height=150, label_visibility="collapsed")
        if cover_val != project.cover_prompt:
            project.cover_prompt = cover_val
            save_project(project)
            
        st.divider()
        
        st.subheader("Chapter Artwork")
        st.markdown("Generate image prompts for the start of each completed chapter.")
        
        completed_chapters = [c for c in project.chapters if c.is_completed]
        if not completed_chapters:
            st.info("No completed chapters yet. Finish drafting some chapters in Phase 3 first.")
        else:
            for idx, chapter in enumerate(completed_chapters):
                with st.expander(f"Chapter {chapter.number}: {chapter.title or 'Untitled'}"):
                    st.caption("Summary:")
                    st.write(chapter.summary)
                    
                    if st.button(f"Generate Prompt for Chapter {chapter.number}", key=f"gen_prompt_{chapter.number}"):
                        with st.spinner("Generating chapter prompt..."):
                            chapter.image_prompt = image_agent.generate_chapter_prompt(chapter, project)
                            save_project(project)
                            st.rerun()
                            
                    if chapter.image_prompt:
                        prompt_val = st.text_area(
                            "Image Prompt", 
                            value=chapter.image_prompt, 
                            height=100, 
                            key=f"text_prompt_{chapter.number}"
                        )
                        if prompt_val != chapter.image_prompt:
                            chapter.image_prompt = prompt_val
                            save_project(project)
