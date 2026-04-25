"""
Persistence layer for BookBot_07.
Handles saving and loading the ProjectState.
"""

import json
import os
from src.core.state import ProjectState

DATA_DIR = "data"

def save_project(state: ProjectState, filename: str = "project_state.json"):
    """Saves the project state to a JSON file."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(state.model_dump_json(indent=4))

def load_project(filename: str = "project_state.json") -> ProjectState:
    """Loads the project state from a JSON file."""
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        return ProjectState()
    
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        return ProjectState(**data)
