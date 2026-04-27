import chromadb
import os
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
import re
from typing import List, Tuple, Dict, Any

class Librarian:
    def __init__(self, vdb_path: str, collection_name: str = "library"):
        self.client = chromadb.PersistentClient(path=vdb_path)
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def sanitize_title(self, title: str) -> str:
        """Matches FilingBot's ID generation logic."""
        return "".join(c for c in str(title) if c.isalnum())

    def calculate_metrics(self, chunks: List[str]) -> float:
        """Calculates average sentence length in words."""
        all_text = " ".join(chunks)
        # Split by typical sentence enders
        sentences = re.split(r'[.!?]+', all_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        if not sentences:
            return 0.0
        
        word_counts = [len(s.split()) for s in sentences]
        return round(sum(word_counts) / len(word_counts), 1)

    def get_windowed_context(self, query: str, n_window: int = 1) -> Tuple[List[str], Dict[str, Any]]:
        """Retrieves best match and its neighbors from the same book."""
        results = self.collection.query(query_texts=[query], n_results=1)
        if not results["metadatas"] or not results["metadatas"][0]:
            return [], {}
            
        top_meta = results["metadatas"][0][0]
        title = top_meta.get("title", "unknown")
        clean_title = self.sanitize_title(title)
        idx = top_meta.get("book_chunk_index")
        
        if idx is None:
             return results["documents"][0], top_meta

        # Pull surrounding chunks from the same book
        window_ids = [f"{clean_title}_{i}" for i in range(idx - n_window, idx + n_window + 1) if i >= 0]
        fetched = self.collection.get(ids=window_ids)
        
        if not fetched["documents"]:
            return results["documents"][0], top_meta
            
        # Sort documents by index to maintain order
        docs_with_ids = list(zip(fetched["ids"], fetched["documents"]))
        # ID format is "Title_Index" - sort by the numeric part
        docs_with_ids.sort(key=lambda x: int(x[0].split('_')[-1]))
        
        ordered_docs = [d for i, d in docs_with_ids]
        
        # Add dynamic metrics to metadata for prompt building
        top_meta["avg_sentence_len"] = f"{self.calculate_metrics(ordered_docs)} words"
        
        return ordered_docs, top_meta

def build_style_prompt(user_request: str, chunks: List[str], meta: Dict[str, Any]) -> str:
    """Constructs a style-explicit prompt based on retrieved context."""
    context = "\n\n---\n\n".join(chunks)
    author = meta.get('author') or 'the reference author'
    pov = meta.get('pov') or 'the reference POV'
    tone = meta.get('tone') or 'the reference tone'
    avg_len = meta.get('avg_sentence_len') or 'various'
    title = meta.get('title') or 'Reference'
    
    return f"""You are writing in the style of {author}.

Style notes:
- Point of view: {pov}
- Tone: {tone}
- Sentence length: {avg_len} (match this rhythm closely)
- Vocabulary register: match the diction in the context below — do not modernise or simplify it

Context (from {title}):
{context}

Task:
{user_request}

Write strictly in the style demonstrated above. Do not narrate or explain; just write."""
