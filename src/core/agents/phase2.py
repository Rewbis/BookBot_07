"""
Phase 2 Agents: Scene Writer and Continuity Checker.
Responsible for creating detailed chapter outlines.
"""

import json
from typing import Dict, Any, List
from src.core.llm import get_llm
from src.core.state import ProjectState, Chapter
from src.core.utils import clean_json_response

class Phase2SceneWriter:
    """The Scene Writer agent responsible for creating chapter outlines."""
    
    def __init__(self):
        self.llm = get_llm()

    def generate_chapter_outlines(self, state: ProjectState) -> List[Dict[str, Any]]:
        """
        Generates outlines for all chapters based on the book plan and data elements.
        """
        system_prompt = (
            "You are an expert Outliner. Your goal is to break down a book plan into detailed chapter outlines.\n"
            "You must strictly adhere to the names, roles, and descriptions provided in the WORLD BIBLE. "
            "Do not change character names, location names, or key event details.\n\n"
            "For each chapter, provide a title, a detailed outline, and side notes. "
            "Side notes MUST explicitly list characters involved (e.g., 'Characters: Alice, Bob').\n\n"
            "Return your response in strict JSON format as a list of objects with keys: "
            "[number, title, outline, side_notes, rough_wordcount]."
        )
        
        char_info = "\n".join([f"- {c.name} ({c.role}): {c.description}" for c in state.characters])
        loc_info = "\n".join([f"- {l.name}: {l.description}" for l in state.locations])
        ev_info = "\n".join([f"- {e.title}: {e.description}" for e in state.events])
        
        context = (
            f"Book Plan: {state.book_plan}\n"
            f"Target Chapters: {state.target_chapters}\n\n"
            f"WORLD BIBLE (Characters):\n{char_info}\n\n"
            f"WORLD BIBLE (Locations):\n{loc_info}\n\n"
            f"WORLD BIBLE (Key Events):\n{ev_info}\n"
        )
        
        user_prompt = f"Context:\n{context}\n\nPlease generate outlines for {state.target_chapters} chapters."
        
        response = self.llm.invoke([("system", system_prompt), ("human", user_prompt)])
        return self._parse_json_list(response.content)

    def refine_outlines(self, state: ProjectState, feedback: str) -> List[Dict[str, Any]]:
        """Refines outlines based on continuity feedback."""
        system_prompt = (
            "You are an expert Outliner. Revise the chapter outlines based on the continuity feedback provided.\n"
            "Ensure the narrative flow is consistent and addresses the issues raised.\n\n"
            "Return the revised list in strict JSON format."
        )
        
        context = f"Continuity Feedback: {feedback}\n\nCurrent Outlines: {[c.outline for c in state.chapters]}"
        response = self.llm.invoke([("system", system_prompt), ("human", context)])
        return self._parse_json_list(response.content)

    def regenerate_subsequent_chapters(self, state: ProjectState, fixed_chapter_index: int) -> List[Dict[str, Any]]:
        """
        Re-generates chapters from fixed_chapter_index + 1 to the end, 
        using previous chapters as fixed context.
        """
        system_prompt = (
            "You are an expert Outliner. Your goal is to re-generate the remaining chapter outlines of a book "
            "based on a set of FIXED previous chapters and the overall book plan.\n"
            "You must strictly adhere to the WORLD BIBLE and maintain continuity from the fixed chapters.\n\n"
            "Return your response in strict JSON format as a list of objects for the REMAINING chapters only. "
            "Side notes MUST explicitly list characters involved (e.g., 'Characters: Alice, Bob').\n"
            "Each object must have keys: [number, title, outline, side_notes, rough_wordcount]."
        )
        
        fixed_chapters = state.chapters[:fixed_chapter_index + 1]
        fixed_context = "\n".join([
            f"Chapter {c.number} (FIXED):\nTitle: {c.title}\nOutline: {c.outline}\nSide Notes: {c.side_notes}" 
            for c in fixed_chapters
        ])
        
        char_info = "\n".join([f"- {c.name} ({c.role}): {c.description}" for c in state.characters])
        loc_info = "\n".join([f"- {l.name}: {l.description}" for l in state.locations])
        ev_info = "\n".join([f"- {e.title}: {e.description}" for e in state.events])
        
        context = (
            f"Book Plan: {state.book_plan}\n\n"
            f"WORLD BIBLE (Characters):\n{char_info}\n\n"
            f"WORLD BIBLE (Locations):\n{loc_info}\n\n"
            f"WORLD BIBLE (Key Events):\n{ev_info}\n\n"
            f"FIXED CHAPTERS (DO NOT CHANGE THESE):\n{fixed_context}\n"
        )
        
        actual_chapters = len(state.chapters)
        remaining_count = actual_chapters - (fixed_chapter_index + 1)
        if remaining_count <= 0:
            return []
            
        user_prompt = (
            f"Context:\n{context}\n\n"
            f"Please generate outlines for the remaining {remaining_count} chapters (starting from Chapter {fixed_chapter_index + 2})."
        )
        
        response = self.llm.invoke([("system", system_prompt), ("human", user_prompt)])
        return self._parse_json_list(response.content)

    def _parse_json_list(self, content: str) -> List[Dict[str, Any]]:
        result = clean_json_response(content)
        if isinstance(result, list):
            return result
        return []

class Phase2ContinuityChecker:
    """The Continuity Checker agent responsible for ensuring coherence between chapters."""
    
    def __init__(self):
        self.llm = get_llm()

    def check_continuity(self, state: ProjectState) -> str:
        """
        Checks the chapter outlines for continuity errors or pacing issues.
        """
        system_prompt = (
            "You are a Continuity Expert. Review the chapter outlines for a book and identify any "
            "logical inconsistencies, character contradictions, or timeline errors."
        )
        
        outlines = "\n".join([f"Ch {c.number}: {c.outline}" for c in state.chapters])
        user_prompt = f"Chapter Outlines:\n{outlines}\n\nPerform a continuity check."
        
        response = self.llm.invoke([("system", system_prompt), ("human", user_prompt)])
        return response.content
