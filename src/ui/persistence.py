"""
Persistence layer for BookBot_07.
Handles saving and loading the ProjectState.
"""

import json
import os
from datetime import datetime
import re
from src.core.state import ProjectState

DATA_DIR = "data"

def save_project(state: ProjectState, filename: str = "project_state.json", use_timestamp: bool = False):
    """Saves the project state to a JSON file."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    # Update metadata
    state.last_updated = datetime.now().isoformat()
    
    if use_timestamp:
        # Sanitize book idea for filename if no title exists
        title = state.book_idea[:20] if state.book_idea else "Untitled"
        title = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"{title}_{timestamp}.json"
        
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(state.model_dump_json(indent=4))
    return filename

def load_project(filename: str = "project_state.json") -> ProjectState:
    """Loads the project state from a JSON file."""
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        return ProjectState()
    
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        return ProjectState(**data)
