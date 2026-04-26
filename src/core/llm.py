"""
LLM interface for BookBot_07.
Uses langchain_ollama to interact with local Ollama models.
"""

from langchain_ollama import ChatOllama
from langchain_core.callbacks import BaseCallbackHandler
from typing import Optional, Any, Dict, List
import streamlit as st

class TokenUsageCallback(BaseCallbackHandler):
    """Callback to capture token usage and update st.session_state."""
    def on_llm_end(self, response: Any, **kwargs: Any) -> Any:
        try:
            # langchain_ollama provides usage_metadata in the last generation
            if hasattr(response, 'generations') and response.generations:
                last_gen = response.generations[-1][0]
                if hasattr(last_gen, 'message') and hasattr(last_gen.message, 'usage_metadata'):
                    usage = last_gen.message.usage_metadata
                    if usage:
                        st.session_state.telemetry["prompt_tokens"] += usage.get("input_tokens", 0)
                        st.session_state.telemetry["completion_tokens"] += usage.get("output_tokens", 0)
                        st.session_state.telemetry["total_tokens"] += usage.get("total_tokens", 0)
        except Exception:
            pass # Silent fail to avoid crashing the writing process

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
        callbacks=[TokenUsageCallback()]
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
