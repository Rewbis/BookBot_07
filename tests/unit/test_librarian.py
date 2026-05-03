import pytest
import tempfile
import os
from src.core.librarian import Librarian

@pytest.fixture
def librarian():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp_dir:
        yield Librarian(vdb_path=temp_dir, collection_name="test_library")

def test_sanitize_title(librarian):
    assert librarian.sanitize_title("Book: The Great! Adventure_123") == "BookTheGreatAdventure123"
    assert librarian.sanitize_title("1984") == "1984"

def test_calculate_metrics(librarian):
    # Calculate metrics is average sentence length
    chunks = [
        "This is a short sentence.", # 5 words
        "Here is another one, slightly longer!" # 6 words
    ]
    # Total 11 words, 2 sentences -> 5.5
    assert librarian.calculate_metrics(chunks) == 5.5
    
    assert librarian.calculate_metrics([]) == 0.0
    assert librarian.calculate_metrics(["No punctuation here"]) == 3.0 # 1 sentence, 3 words

def test_get_windowed_context(librarian):
    # Populate the collection
    docs = [
        "Chapter 1 start.",
        "Chapter 1 middle.",
        "Chapter 1 end.",
        "Chapter 2 start."
    ]
    metadatas = [
        {"title": "My Book", "book_chunk_index": 0, "author": "Me"},
        {"title": "My Book", "book_chunk_index": 1, "author": "Me"},
        {"title": "My Book", "book_chunk_index": 2, "author": "Me"},
        {"title": "My Book", "book_chunk_index": 3, "author": "Me"}
    ]
    ids = ["MyBook_0", "MyBook_1", "MyBook_2", "MyBook_3"]
    
    librarian.collection.add(documents=docs, metadatas=metadatas, ids=ids)
    
    # Query for "middle", should return index 1
    # window=1 should return 0, 1, 2
    context, meta = librarian.get_windowed_context("Chapter 1 middle", n_window=1)
    
    assert len(context) == 3
    assert context == ["Chapter 1 start.", "Chapter 1 middle.", "Chapter 1 end."]
    assert meta["title"] == "My Book"
    assert "avg_sentence_len" in meta

def test_get_windowed_context_edges(librarian):
    docs = [
        "Start.", "Middle.", "End."
    ]
    metadatas = [
        {"title": "Book2", "book_chunk_index": 0},
        {"title": "Book2", "book_chunk_index": 1},
        {"title": "Book2", "book_chunk_index": 2}
    ]
    ids = ["Book2_0", "Book2_1", "Book2_2"]
    librarian.collection.add(documents=docs, metadatas=metadatas, ids=ids)
    
    # Query "Start.", idx 0. window=1 -> should only get 0, 1 (no -1)
    context, _ = librarian.get_windowed_context("Start.", n_window=1)
    assert context == ["Start.", "Middle."]
    
    # Query "End.", idx 2. window=1 -> should only get 1, 2 (no 3)
    context, _ = librarian.get_windowed_context("End.", n_window=1)
    assert context == ["Middle.", "End."]
