import pytest
from src.core.utils import clean_json_response, clean_prose_response, parse_range_string, clean_element

@pytest.mark.parametrize("raw,expected_type,expected_content", [
    ('<think>reasoning</think>\n{"plan": "x"}', dict, {"plan": "x"}),
    ('<think>unclosed\n[{"number": 1}]', list, [{"number": 1}]),
    ('```json\n{"plan": "x"}\n```', dict, {"plan": "x"}),
    ('{"plan": "it\u2019s fine"}', dict, {"plan": "it\u2019s fine"}),  # smart apostrophe
    ('Some leading text\n```json\n{"a": 1}\n```\nSome trailing text', dict, {"a": 1}),
    ('{"broken": "json", }', dict, {"broken": "json"}),
    ('[{"a": 1}, {"b": 2}]', list, [{"a": 1}, {"b": 2}]),
])
def test_clean_json_response(raw, expected_type, expected_content):
    result = clean_json_response(raw)
    assert isinstance(result, expected_type)
    assert result == expected_content

def test_clean_json_response_not_json():
    result = clean_json_response("Not JSON at all")
    # json_repair returns an empty string when it gives up on plain text
    assert result == ""

def test_clean_prose_response_behavior():
    # Regular case
    assert clean_prose_response("<think>hmm</think>\nProse!") == "Prose!"
    
    # Markdown
    assert clean_prose_response("```markdown\nText\n```") == "Text"
    assert clean_prose_response("```\nText\n```") == "Text"
    
    # Just text
    assert clean_prose_response("Just text") == "Just text"
    
    # Unclosed thinking tag
    # In current utils.py, if <think> is unclosed, it doesn't remove the text after it, just the tag itself.
    assert clean_prose_response("<think>unclosed reasoning\nProse!") == "unclosed reasoning\nProse!"

@pytest.mark.parametrize("raw,max_val,expected", [
    ('1-5, 8, 10-12', 15, [1, 2, 3, 4, 5, 8, 10, 11, 12]),
    ('1-3', 2, [1, 2]), # max_val is 2, so 3 is excluded
    ('invalid, 1', 10, [1]),
    ('', 10, []),
    ('10-8', 10, []), # start > end, range doesn't execute
    (' 1 , 2 - 3 ', 5, [1, 2, 3]),
])
def test_parse_range_string(raw, max_val, expected):
    assert parse_range_string(raw, max_val) == expected

def test_clean_element():
    assert clean_element({"name": "Bob", "age": None}) == {"name": "Bob"}
    assert clean_element("Bob") == {"name": "Bob"}
    assert clean_element("Bob", default_key="character") == {"character": "Bob"}
    assert clean_element(123) == {}
