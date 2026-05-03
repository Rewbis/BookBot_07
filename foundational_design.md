# Foundational Design: BookBot_07

A definitive design source for the BookBot Narrative Engine. This document preserves system purpose, architectural decisions, and project boundaries across development sessions.

## 1. System Purpose
BookBot_07 follows a **Phased Pipeline with Shared State**, where specialized agents assist the author through a 4-phase lifecycle.

## 2. Scope Boundaries (MoSCoW)

### Must Have
- 4 phases of writing: Planning, Outlining, Drafting, Publishing. Each with AI agents dedicated to its completion, assisting the human user and working together to create the best possible book.
- **Phased Pipeline**: A clear 4-phase progression from Planning to Publishing.
- **4-Pass Drafting**: A sequential sculpting process: **Action -> Sensory -> Voice -> Editor**.
- **Local Sovereignty**: All LLM processing hosted locally via **Ollama**.
- **Registry System**: Centralized state management via `ProjectState` with full snapshot save/load functionality.

### Should Have
- **Phase 4: Publishing & Marketing**: Agents for generating image prompts (cover/chapters), blurbs, and marketing copy.

### Nice to Have
- **Autonomous Research**: Integration with **Tavily** for world-building fact-checking.

### Won't Have (v0.6)
- **Direct Publishing**: Automated upload to KDP/IngramSpark.
- **Cloud-Only Hosting**: Strictly avoids reliance on proprietary black-box APIs for core logic.

## 3. Architecture Summary
- **UI Layer**: Streamlit-based dashboard organized into clear tabs/phases.
- **Logic Layer (Narrative Engine)**: A phased pipeline fleet of specialized agents orchestrated by LangGraph, utilizing a shared state registry for cross-phase continuity.
- **Persistence Layer**: JSON-based full-project snapshots via `ProjectState` and world bible.

Further details can be found in [docs/architecture.md](file:///e:/Coding/BookBot_07/docs/architecture.md).

## 4. Key Design Decisions (KDD)
- **Design Decision 01: Phased Execution**: We follow a strict 4-phase linear progression. Agents are context-aware and pull from the shared World Bible to maintain continuity across phases.
- **Design Decision 02: Multi-Pass Layering**: Prose is never generated in one go. It is "sculpted" through sequential passes (Action -> Sensory -> Voice -> Editor) to ensure quality and stylistic consistency.
- **Design Decision 03: Adversarial Validation**: Creative outputs in Phase 1 and 2 are checked by a Critic or ContinuityChecker before being finalized.
- **Design Decision 04: Structured Lore (The Bible)**: Characters, locations, and events are stored as structured entities with tracked attributes to prevent hallucinations.
- **Design Decision 05: Logic-First Parsing**: We avoid "prompt-engineering" for data format compliance. We use regex and deterministic Python to extract JSON from LLM noise.

## 5. Document Navigation
- [Architecture & Tech Stack](file:///e:/Coding/BookBot_07/docs/architecture.md)
- [Narrative Workflow](file:///e:/Coding/BookBot_07/docs/narrative_workflow.md)
- [RAID Log (Risks & Assumptions)](file:///e:/Coding/BookBot_07/docs/raid_log.md)
- [Anti-Patterns & Lessons Learned](file:///e:/Coding/BookBot_07/docs/anti_patterns.md)
- [Roadmap & Backlog](file:///e:/Coding/BookBot_07/roadmap.md)
