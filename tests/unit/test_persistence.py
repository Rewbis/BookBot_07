import pytest
import os
import tempfile
from unittest.mock import patch
from src.core.state import ProjectState, Chapter, Character
from src.ui.persistence import save_project, load_project, DATA_DIR

@pytest.fixture
def mock_data_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('src.ui.persistence.DATA_DIR', temp_dir):
            yield temp_dir

def test_save_and_load_project(mock_data_dir):
    # Create a state with some populated fields to ensure they survive round-trip
    original_state = ProjectState(
        book_idea="A great test book",
        target_chapters=5,
        characters=[Character(name="Alice", role="Hero", traits=["brave"])],
        chapters=[Chapter(number=1, title="Beginnings", draft="It was a dark and stormy night.")]
    )
    
    # Save the project
    filename = save_project(original_state, filename="test_roundtrip.json")
    
    # Load it back
    loaded_state = load_project(filename)
    
    # Exclude last_updated from comparison because save_project modifies it
    original_dict = original_state.model_dump()
    loaded_dict = loaded_state.model_dump()
    
    # The loaded state will have the timestamp set during save, so sync them up for assertion
    original_dict['last_updated'] = loaded_dict['last_updated']
    
    assert loaded_dict == original_dict
    assert loaded_state.chapters[0].title == "Beginnings"
    assert loaded_state.characters[0].name == "Alice"

def test_load_project_not_found(mock_data_dir):
    # Should return a new empty ProjectState if file doesn't exist
    state = load_project("does_not_exist.json")
    assert isinstance(state, ProjectState)
    assert state.book_idea == ""
    assert len(state.chapters) == 0
