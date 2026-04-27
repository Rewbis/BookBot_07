"""
State models for BookBot_07.
Defines the project structure and data elements.
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class StyleProfile(BaseModel):
    """Defines the writing style for the book."""
    tone: str = ""           # e.g. "dark and lyrical"
    pov: str = ""            # e.g. "third person limited"
    sample_prose: str = ""   # author pastes 200 words they like
    use_rag: bool = False
    reference_vdb: str = ""  # folder name in style_VDBs
    reference_author: str = ""
    n_window: int = 1

class Character(BaseModel):
    """Represents a character in the book."""
    name: str = "Unknown"
    role: str = "Protagonist"
    description: str = ""
    traits: List[str] = Field(default_factory=list)
    arc: Optional[str] = None

class Location(BaseModel):
    """Represents a location in the book."""
    name: str = "Unknown Location"
    description: str = ""
    significance: Optional[str] = None

class Event(BaseModel):
    """Represents a key event in the book's timeline."""
    title: str = "Untitled Event"
    description: str = ""
    location_name: Optional[str] = None
    involved_characters: List[str] = Field(default_factory=list)

class Chapter(BaseModel):
    """Represents a chapter outline and its drafted content."""
    number: int
    title: Optional[str] = None
    rough_wordcount: int = 1500
    outline: Optional[str] = None
    side_notes: Optional[str] = None
    draft: Optional[str] = None
    summary: str = "" # Short context for continuity
    is_completed: bool = False

class ProjectState(BaseModel):
    """The global state of the BookBot project."""
    # Phase 1: Planning
    book_idea: str = ""
    book_plan: str = ""
    premise: str = "" # Short summary for drafting context
    target_chapters: int = 20
    target_total_wordcount: int = 50000
    style_profile: StyleProfile = Field(default_factory=StyleProfile)
    
    # Data Elements (World Bible)
    characters: List[Character] = Field(default_factory=list)
    locations: List[Location] = Field(default_factory=list)
    events: List[Event] = Field(default_factory=list)
    
    # Phase 2: Outlining
    chapters: List[Chapter] = Field(default_factory=list)
    
    # Phase 3: Drafting
    current_chapter_index: int = 0
    
    # Metadata
    current_phase: int = 1  # 1: Planning, 2: Outlining, 3: Drafting
    last_updated: str = ""
    
    def get_character_names(self) -> List[str]:
        """Returns a list of character names."""
        return [c.name for c in self.characters]

    def get_location_names(self) -> List[str]:
        """Returns a list of location names."""
        return [l.name for l in self.locations]
