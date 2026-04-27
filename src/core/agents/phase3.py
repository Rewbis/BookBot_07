"""
Phase 3 Agents: Action, Sensory, Voice, and Editor.
Responsible for drafting full scenes.
"""

from src.core.llm import get_llm
from src.core.state import ProjectState, Chapter
import os
from src.core.librarian import Librarian, build_style_prompt

class Phase3ActionAgent:
    """Focuses on the core action and movement within a scene."""
    def __init__(self):
        self.llm = get_llm()

    def write_action(self, state: ProjectState, chapter: Chapter, prev_context: str = "") -> str:
        system_prompt = (
            f"You are writing Chapter {chapter.number} of {state.target_chapters} ONLY. "
            f"Focus on the physical movements, dialogue, and direct actions in the scene. "
            f"Do not resolve plot threads beyond this chapter. Do not write endings or conclusions "
            f"unless this chapter's outline specifically requires one. Stop when the chapter's outlined "
            f"events are complete.\n\n"
            f"Target length: approximately {chapter.rough_wordcount} words.\n"
            f"Return ONLY the story prose. Do not include any preamble, conversational filler, or markdown code block markers."
        )
        context = (
            f"Chapter {chapter.number}: {chapter.title}\n"
            f"Premise: {state.premise}\n"
            f"Chapter Outline: {chapter.outline}\n"
            f"Side Notes: {chapter.side_notes}\n\n"
            f"{prev_context}"
        )
        return self.llm.invoke([("system", system_prompt), ("human", context)]).content

class Phase3SensoryAgent:
    """Enhances the scene with sensory details (sight, sound, smell, etc.)."""
    def __init__(self):
        self.llm = get_llm()

    def add_sensory_details(self, draft: str, side_notes: str) -> str:
        system_prompt = (
            f"You are a Sensory Specialist. Enhance the provided draft with vivid sensory details (sight, sound, smell, touch, taste) based on the side notes. "
            f"Return ONLY the updated story prose. Do not include any preamble, conversational filler, or markdown code block markers."
        )
        user_prompt = f"Side Notes: {side_notes}\n\nDraft:\n{draft}"
        return self.llm.invoke([("system", system_prompt), ("human", user_prompt)]).content

class Phase3VoiceAgent:
    """Ensures consistent character voice and tone."""
    def __init__(self):
        self.llm = get_llm()

    def apply_voice(self, draft: str, project: ProjectState, side_notes: str, outline: str = "") -> str:
        style = project.style_profile
        
        if style.use_rag and style.reference_vdb:
            vdb_path = os.path.join("style_VDBs", style.reference_vdb)
            if os.path.exists(vdb_path):
                lib = Librarian(vdb_path)
                # Use side_notes as query to find relevant style context
                query = side_notes if side_notes else draft[:500]
                chunks, meta = lib.get_windowed_context(query, n_window=style.n_window)
                
                if chunks:
                    system_prompt = build_style_prompt(
                        "Refine the draft to ensure characters speak and act consistently with their traits and the overall tone of the book.",
                        chunks,
                        meta
                    )
                    # Add character info to the prompt as well
                    mentioned_chars = self._get_mentioned_characters(project, side_notes, outline, draft)
                    char_info = ""
                    if mentioned_chars:
                        char_info = "\n".join([f"{c.name}: {c.traits}" for c in mentioned_chars])
                        system_prompt += f"\n\nCharacters in this scene:\n{char_info}"
                    
                    system_prompt += "\n\nReturn ONLY the updated story prose. Do not include any preamble, conversational filler, or markdown code block markers."
                    
                    return self.llm.invoke([("system", system_prompt), ("human", draft)]).content

        # Fallback to standard prompt if RAG is disabled or failed
        system_prompt = (
            f"You are a Voice and Tone Expert. Refine the draft to ensure characters speak and act consistently with their traits and the overall tone of the book.\n\n"
            f"For each significant character action, ensure the prose conveys WHY they are doing it — "
            f"their emotional state or motivation should be implicit in their behaviour, not stated directly."
            f"REQUIRED STYLE:\n- Tone: {style.tone}\n- POV: {style.pov}\n"
            f"PROSE SAMPLE (for inspiration): {style.sample_prose}\n\n"
            f"Return ONLY the updated story prose. Do not include any preamble, conversational filler, or markdown code block markers."
        )
        mentioned_chars = self._get_mentioned_characters(project, side_notes, outline, draft)
        char_info = ""
        if mentioned_chars:
            char_info = "Characters in this scene:\n" + "\n".join([f"{c.name}: {c.traits}" for c in mentioned_chars])
        
        user_prompt = f"{char_info}\n\nDraft:\n{draft}"
        return self.llm.invoke([("system", system_prompt), ("human", user_prompt)]).content

    def _get_mentioned_characters(self, project: ProjectState, side_notes: str, outline: str = "", draft: str = ""):
        mentioned_chars = []
        combined_text = (side_notes + " " + outline + " " + draft).lower()
        for c in project.characters:
            if c.name.lower() in combined_text:
                mentioned_chars.append(c)
        return mentioned_chars

class Phase3EditorAgent:
    """Performs final polish, grammar checks, and pacing adjustments."""
    def __init__(self):
        self.llm = get_llm()

    def final_edit(self, draft: str, project: ProjectState) -> str:
        style = project.style_profile
        system_prompt = (
            f"You are a Senior Editor. Perform a final polish of the scene, fixing flow, grammar, and pacing issues. "
            f"Avoid: overused descriptors, excessive similes and metaphors, and ornate language that "
            f"obscures action. Prefer concrete sensory detail over abstract flourish. One strong image "
            f"beats three weak ones."
            f"Ensure the prose adheres to the target style: {style.tone} in {style.pov}.\n\n"
            f"Return ONLY the polished story prose. Do not include any preamble, conversational filler, or markdown code block markers."
        )
        return self.llm.invoke([("system", system_prompt), ("human", draft)]).content

    def summarise_chapter(self, draft: str) -> str:
        """Generates a concise 3-sentence summary of the chapter for continuity context."""
        system_prompt = (
            f"You are a narrative analyst. Summarise this chapter in exactly 3 sentences: "
            f"what happened, who was involved, and where it ended emotionally. "
            f"Focus on information crucial for the next chapter's continuity."
        )
        # Use a smaller context for this fast call
        return self.llm.invoke([("system", system_prompt), ("human", draft)]).content
