"""
Phase 1 Agents: Plotter and Critic.
Responsible for brainstorming and refining the book plan and world elements.
"""

import json
from typing import Dict, Any, List
from src.core.llm import get_llm
from src.core.state import ProjectState, Character, Location, Event
from src.core.utils import clean_json_response

class Phase1Plotter:
    """The Plotter agent responsible for creating the initial book plan."""
    
    def __init__(self):
        self.llm = get_llm()

    def generate_initial_plan(self, idea: str) -> Dict[str, Any]:
        """
        Generates an initial book plan and data elements from a book idea.
        """
        system_prompt = (
            "You are an expert Book Plotter. Your goal is to take a book idea and expand it into a "
            "coherent plan. You must also identify key characters, locations, and events.\n\n"
            "Return your response in strict JSON format with the following keys:\n"
            "- plan: A detailed narrative overview of the book.\n"
            "- characters: A list of objects with [name, role, description, traits (list), arc].\n"
            "- locations: A list of objects with [name, description, significance].\n"
            "- events: A list of objects with [title, description, location_name, involved_characters (list)].\n"
        )
        
        user_prompt = f"Book Idea: {idea}\n\nPlease generate a comprehensive plan and world data."
        
        response = self.llm.invoke([("system", system_prompt), ("human", user_prompt)])
        return self._parse_json(response.content)

    def refine_plan(self, current_state: ProjectState, feedback: str) -> Dict[str, Any]:
        """
        Refines the plan based on feedback from the Critic.
        """
        system_prompt = (
            "You are an expert Book Plotter. You have received feedback from a Critic on your plan. "
            "Revise the plan and world elements to address the feedback while maintaining the core vision.\n\n"
            "Return your response in strict JSON format with the same keys as before: [plan, characters, locations, events]."
        )
        
        context = (
            f"Current Plan: {current_state.book_plan}\n"
            f"Characters: {[c.name for c in current_state.characters]}\n"
            f"Critic Feedback: {feedback}"
        )
        
        response = self.llm.invoke([("system", system_prompt), ("human", context)])
        return self._parse_json(response.content)

    def _parse_json(self, content: str) -> Dict[str, Any]:
        """Helper to extract and parse JSON from LLM response."""
        result = clean_json_response(content)
        if isinstance(result, dict):
            return result
        return {"plan": content, "characters": [], "locations": [], "events": []}

class Phase1Critic:
    """The Critic agent responsible for reviewing the book plan."""
    
    def __init__(self):
        self.llm = get_llm()

    def review_plan(self, plan: str, characters: List[Character]) -> str:
        """
        Reviews the plan and characters for coherence, depth, and pacing.
        """
        system_prompt = (
            "You are a professional Book Critic and Editor. Your job is to find weaknesses in a "
            "book plan. Look for plot holes, flat characters, or pacing issues. Be constructive but firm."
        )
        
        char_info = "\n".join([f"- {c.name} ({c.role}): {c.description}" for c in characters])
        user_prompt = f"Book Plan: {plan}\n\nCharacters:\n{char_info}\n\nProvide your critical assessment."
        
        response = self.llm.invoke([("system", system_prompt), ("human", user_prompt)])
        return response.content
