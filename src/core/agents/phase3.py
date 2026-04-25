"""
Phase 3 Agents: Action, Sensory, Voice, and Editor.
Responsible for drafting full scenes.
"""

from src.core.llm import get_llm
from src.core.state import ProjectState, Chapter

class Phase3ActionAgent:
    """Focuses on the core action and movement within a scene."""
    def __init__(self):
        self.llm = get_llm()

    def write_action(self, state: ProjectState, chapter: Chapter, prev_context: str = "") -> str:
        system_prompt = (
            "You are an Action-Oriented Writer. Focus on the physical movements, dialogue, and direct actions in the scene. "
            f"Target length: approximately {chapter.rough_wordcount} words. "
            "Return ONLY the story prose. Do not include any preamble, conversational filler, or markdown code block markers."
        )
        context = (
            f"Chapter {chapter.number}: {chapter.title}\n"
            f"Book Plan: {state.book_plan}\n"
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
            "You are a Sensory Specialist. Enhance the provided draft with vivid sensory details (sight, sound, smell, touch, taste) based on the side notes. "
            "Return ONLY the updated story prose. Do not include any preamble, conversational filler, or markdown code block markers."
        )
        user_prompt = f"Side Notes: {side_notes}\n\nDraft:\n{draft}"
        return self.llm.invoke([("system", system_prompt), ("human", user_prompt)]).content

class Phase3VoiceAgent:
    """Ensures consistent character voice and tone."""
    def __init__(self):
        self.llm = get_llm()

    def apply_voice(self, draft: str, characters: list) -> str:
        system_prompt = (
            "You are a Voice and Tone Expert. Refine the draft to ensure characters speak and act consistently with their traits and the overall tone of the book. "
            "Return ONLY the updated story prose. Do not include any preamble, conversational filler, or markdown code block markers."
        )
        char_info = "\n".join([f"{c.name}: {c.traits}" for c in characters])
        user_prompt = f"Characters:\n{char_info}\n\nDraft:\n{draft}"
        return self.llm.invoke([("system", system_prompt), ("human", user_prompt)]).content

class Phase3EditorAgent:
    """Performs final polish, grammar checks, and pacing adjustments."""
    def __init__(self):
        self.llm = get_llm()

    def final_edit(self, draft: str) -> str:
        system_prompt = (
            "You are a Senior Editor. Perform a final polish of the scene, fixing flow, grammar, and pacing issues. "
            "Return ONLY the polished story prose. Do not include any preamble, conversational filler, or markdown code block markers."
        )
        return self.llm.invoke([("system", system_prompt), ("human", draft)]).content
