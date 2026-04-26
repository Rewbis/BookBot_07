"""
LLM interface for BookBot_07.
Uses langchain_ollama to interact with local Ollama models.
"""

from langchain_ollama import ChatOllama
from typing import Optional

def get_llm(model: str = "richardyoung/qwen3-14b-abliterated:Q4_K_M", temperature: float = 0.7):
    """
    Returns an instance of ChatOllama.
    
    Args:
        model (str): The name of the Ollama model to use.
        temperature (float): The sampling temperature.
        
    Returns:
        ChatOllama: The initialized LLM instance.
    """
    return ChatOllama(
        model=model,
        temperature=temperature,
        num_ctx=32768,  # Large context window for book writing
        repeat_penalty=1.1,
    )

def invoke_llm(prompt: str, system_prompt: Optional[str] = None) -> str:
    """
    Utility function to quickly invoke the LLM with a prompt.
    
    Args:
        prompt (str): The user prompt.
        system_prompt (str, optional): The system prompt.
        
    Returns:
        str: The generated response content.
    """
    llm = get_llm()
    messages = []
    if system_prompt:
        messages.append(("system", system_prompt))
    messages.append(("human", prompt))
    
    response = llm.invoke(messages)
    return response.content
