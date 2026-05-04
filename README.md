# BookBot_07

A modular, agentic book-writing assistant powered by LangChain, LangGraph, Streamlit, and Ollama. - moving to v0.08 ! Abandoning LangChain, looking to make it mobile device accessible + hosted on home pc.

## Features
- **Phase 1: Planning** - Brainstorm ideas and create a book plan.
- **Phase 2: Outlining** - Generate detailed chapter outlines.
- **Phase 3: Drafting** - Write full scenes with a 4-agent pipeline.
- **Local LLM** - Uses Ollama for private, local generation.

## Setup
1. Create and install requirements:
   ```bash
   py -m venv venv
   .\venv\Scripts\python -m pip install -r requirements.txt
   ```
2. Ensure Ollama is running and you have the `richardyoung/qwen3-14b-abliterated:Q4_K_M` model pulled:
   ```bash
   ollama pull richardyoung/qwen3-14b-abliterated:Q4_K_M
   ```
3. Run the app:
   ```bash
   streamlit run src/ui/app.py
   ```

## Development
- `src/core/`: Agents and LangGraph logic.
- `src/ui/`: Streamlit interface.
- `data/`: Project storage.
