"""
LangGraph orchestration for BookBot_07.
"""

import json
from typing import TypedDict, Annotated, List, Union
from langgraph.graph import StateGraph, END
from src.core.state import ProjectState, Character, Location, Event, Chapter
from src.core.agents.phase1 import Phase1Plotter, Phase1Critic
from src.core.agents.phase2 import Phase2SceneWriter, Phase2ContinuityChecker
from src.core.agents.phase3 import Phase3ActionAgent, Phase3SensoryAgent, Phase3VoiceAgent, Phase3EditorAgent
from src.core.utils import clean_prose_response, clean_element

class GraphState(TypedDict):
    """The state of the graph."""
    project: ProjectState
    critic_feedback: str
    iteration_count: int

def plotter_node(state: GraphState) -> GraphState:
    """Initial plotting node."""
    plotter = Phase1Plotter()
    if not state["project"].book_plan:
        result = plotter.generate_initial_plan(state["project"].book_idea)
    else:
        result = plotter.refine_plan(state["project"], state["critic_feedback"])
    
    # Update state
    project = state["project"]
    project.book_plan = result.get("plan", project.book_plan)
    
    project.characters = [Character(**clean_element(c, "name")) for c in result.get("characters", [])]
    project.locations = [Location(**clean_element(l, "name")) for l in result.get("locations", [])]
    project.events = [Event(**clean_element(e, "title")) for e in result.get("events", [])]
    
    return {**state, "project": project, "iteration_count": state["iteration_count"] + 1}

def critic_node(state: GraphState) -> GraphState:
    """Critic review node."""
    critic = Phase1Critic()
    feedback = critic.review_plan(state["project"].book_plan, state["project"].characters)
    return {**state, "critic_feedback": feedback}

def should_continue(state: GraphState) -> str:
    """Router to determine if we should refine or end Phase 1."""
    if state["iteration_count"] >= 2:  # 1 initial + 1 refinement
        return "end"
    return "refine"

def create_phase1_graph():
    """Creates the LangGraph for Phase 1."""
    workflow = StateGraph(GraphState)
    
    workflow.add_node("plotter", plotter_node)
    workflow.add_node("critic", critic_node)
    
    workflow.set_entry_point("plotter")
    
    workflow.add_edge("plotter", "critic")
    
    workflow.add_conditional_edges(
        "critic",
        should_continue,
        {
            "refine": "plotter",
            "end": END
        }
    )
    
    return workflow.compile()

def scene_writer_node(state: GraphState) -> GraphState:
    """Scene writing node."""
    writer = Phase2SceneWriter()
    if not state["project"].chapters or not state["project"].chapters[0].outline:
        results = writer.generate_chapter_outlines(state["project"])
    else:
        results = writer.refine_outlines(state["project"], state["critic_feedback"])
    
    project = state["project"]
    if results:
        # Defensive parsing for chapters
        cleaned_chapters = []
        for i, r in enumerate(results):
            if "number" not in r:
                r["number"] = i + 1
            # Defensive check for side_notes if it comes as a dict
            if "side_notes" in r and isinstance(r["side_notes"], (dict, list)):
                r["side_notes"] = json.dumps(r["side_notes"], indent=2)
            cleaned_chapters.append(Chapter(**r))
        project.chapters = cleaned_chapters
    
    return {**state, "project": project, "iteration_count": state["iteration_count"] + 1}

def continuity_checker_node(state: GraphState) -> GraphState:
    """Continuity check node."""
    checker = Phase2ContinuityChecker()
    feedback = checker.check_continuity(state["project"])
    return {**state, "critic_feedback": feedback}

def create_phase2_graph():
    """Creates the LangGraph for Phase 2."""
    workflow = StateGraph(GraphState)
    
    workflow.add_node("writer", scene_writer_node)
    workflow.add_node("checker", continuity_checker_node)
    
    workflow.set_entry_point("writer")
    
    workflow.add_edge("writer", "checker")
    
    workflow.add_conditional_edges(
        "checker",
        should_continue,
        {
            "refine": "writer",
            "end": END
        }
    )
    
    return workflow.compile()

def action_node(state: GraphState) -> GraphState:
    agent = Phase3ActionAgent()
    project = state["project"]
    chapter = project.chapters[project.current_chapter_index]
    
    prev_context = ""
    if project.current_chapter_index > 0:
        prev = project.chapters[project.current_chapter_index - 1]
        if prev.summary:
            prev_context = f"\nPrevious Chapter Summary:\n{prev.summary}\n"
        elif prev.draft:
            # Fallback if summary is missing but draft exists
            prev_text = prev.draft[-500:]
            prev_context = f"\nPrevious Chapter Outline: {prev.outline}\nLast lines:\n{prev_text}\n"
        
    draft = agent.write_action(project, chapter, prev_context)
    chapter.draft = clean_prose_response(draft)
    return {**state, "project": project}

def sensory_node(state: GraphState) -> GraphState:
    agent = Phase3SensoryAgent()
    project = state["project"]
    chapter = project.chapters[project.current_chapter_index]
    draft = agent.add_sensory_details(chapter.draft, chapter.side_notes)
    chapter.draft = clean_prose_response(draft)
    return {**state, "project": project}

def voice_node(state: GraphState) -> GraphState:
    agent = Phase3VoiceAgent()
    project = state["project"]
    chapter = project.chapters[project.current_chapter_index]
    draft = agent.apply_voice(chapter.draft, project, chapter.side_notes, chapter.outline)
    chapter.draft = clean_prose_response(draft)
    return {**state, "project": project}

def editor_node(state: GraphState) -> GraphState:
    agent = Phase3EditorAgent()
    project = state["project"]
    chapter = project.chapters[project.current_chapter_index]
    draft = agent.final_edit(chapter.draft, project)
    chapter.draft = clean_prose_response(draft)
    return {**state, "project": project}

def summarize_node(state: GraphState) -> GraphState:
    agent = Phase3EditorAgent()
    project = state["project"]
    chapter = project.chapters[project.current_chapter_index]
    summary = agent.summarise_chapter(chapter.draft)
    chapter.summary = summary
    chapter.is_completed = True
    return {**state, "project": project}

def create_phase3_graph():
    """Creates the LangGraph for Phase 3."""
    workflow = StateGraph(GraphState)
    
    workflow.add_node("action", action_node)
    workflow.add_node("sensory", sensory_node)
    workflow.add_node("voice", voice_node)
    workflow.add_node("editor", editor_node)
    workflow.add_node("summarize", summarize_node)
    
    workflow.set_entry_point("action")
    workflow.add_edge("action", "sensory")
    workflow.add_edge("sensory", "voice")
    workflow.add_edge("voice", "editor")
    workflow.add_edge("editor", "summarize")
    workflow.add_edge("summarize", END)
    
    return workflow.compile()

