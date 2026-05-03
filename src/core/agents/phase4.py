"""
Phase 4 Agents: Publishing and Marketing.
Responsible for generating back-cover blurbs, Kindle marketing copy, and image generation prompts.
"""

from src.core.llm import get_llm
from src.core.state import ProjectState, Chapter
from src.core.utils import clean_prose_response

class Phase4MarketingAgent:
    """Agent responsible for generating marketing copy."""
    
    def __init__(self):
        self.llm = get_llm()

    def generate_blurb(self, project: ProjectState) -> str:
        """Generates a punchy back-cover blurb."""
        system_prompt = (
            "You are an expert book publicist. Your goal is to write a compelling, punchy back-cover blurb "
            "that hooks the reader without spoiling the ending. Keep it around 150-200 words. "
            "Focus on the core conflict, the stakes, and the protagonist."
        )
        
        char_info = ", ".join([f"{c.name} ({c.role})" for c in project.characters[:3]])
        context = (
            f"Book Idea: {project.book_idea}\n"
            f"Premise: {project.premise}\n"
            f"Key Characters: {char_info}\n"
            f"Tone: {project.style_profile.tone}"
        )
        
        response = self.llm.invoke([("system", system_prompt), ("human", context)])
        return clean_prose_response(response.content)

    def generate_marketing_copy(self, project: ProjectState) -> str:
        """Generates an Amazon/Kindle-optimized sales description."""
        system_prompt = (
            "You are an expert book marketer specializing in Amazon/Kindle pages. "
            "Write a persuasive, structured sales description for this book. "
            "Use formatting like headlines, bullet points for key selling features, "
            "and a strong call to action at the end. Make it irresistible to the target audience."
        )
        
        context = (
            f"Premise: {project.premise}\n"
            f"Tone: {project.style_profile.tone}\n"
            f"Current Blurb: {project.blurb}\n"
        )
        
        response = self.llm.invoke([("system", system_prompt), ("human", context)])
        return clean_prose_response(response.content)


class Phase4ImageAgent:
    """Agent responsible for generating image prompts for AI generators."""
    
    def __init__(self):
        self.llm = get_llm()

    def derive_image_style(self, project: ProjectState) -> str:
        """Derives a base visual style from the project's tone and sample prose."""
        system_prompt = (
            "You are an expert AI image prompt engineer and art director. "
            "Based on the provided book tone and sample prose, derive a concise 'Visual Style' string "
            "that can be appended to Midjourney or Stable Diffusion prompts. "
            "Examples: 'cinematic lighting, dark fantasy, watercolor, trending on artstation' or "
            "'vibrant cyberpunk, neon lights, 8k resolution, photorealistic'. "
            "Return ONLY the style string, nothing else."
        )
        
        context = (
            f"Tone: {project.style_profile.tone}\n"
            f"Sample Prose: {project.style_profile.sample_prose[:500]}"
        )
        
        response = self.llm.invoke([("system", system_prompt), ("human", context)])
        return clean_prose_response(response.content).strip('\'"')

    def generate_cover_prompt(self, project: ProjectState) -> str:
        """Generates a detailed prompt for a book cover."""
        system_prompt = (
            "You are an expert AI image prompt engineer. Write a highly detailed prompt for an AI image generator "
            "(like Midjourney) to create the cover art for this book. "
            "Focus on the main subject, setting, mood, lighting, and composition. "
            "Do NOT include text/typography instructions, just the art. "
            "End the prompt by appending the exact 'Visual Style' provided."
        )
        
        context = (
            f"Book Idea: {project.book_idea}\n"
            f"Premise: {project.premise}\n"
            f"Visual Style: {project.style_profile.image_style}"
        )
        
        response = self.llm.invoke([("system", system_prompt), ("human", context)])
        return clean_prose_response(response.content)

    def generate_chapter_prompt(self, chapter: Chapter, project: ProjectState) -> str:
        """Generates an image prompt representing the key scene of the chapter."""
        system_prompt = (
            "You are an expert AI image prompt engineer. Write a highly detailed prompt for an AI image generator "
            "to create a single illustration that represents the core action, setting, or mood of this chapter. "
            "Focus on the events taking place at the beginning of the chapter, avoiding spoilers from later in the chapter. "
            "Include the main subject, setting, lighting, and composition. "
            "End the prompt by appending the exact 'Visual Style' provided."
        )
        
        chapter_content = chapter.summary if chapter.summary else chapter.outline
        context = (
            f"Chapter Content: {chapter_content}\n"
            f"Visual Style: {project.style_profile.image_style}"
        )
        
        response = self.llm.invoke([("system", system_prompt), ("human", context)])
        return clean_prose_response(response.content)
