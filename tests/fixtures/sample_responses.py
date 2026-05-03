"""
Sample raw LLM responses to be used in unit tests.
"""

# Contains typical thinking tags and valid JSON
VALID_JSON_WITH_THINKING = '''<think>
I need to output a JSON object with a 'plan' key.
</think>
{
    "plan": "This is a great plan."
}
'''

# Unclosed thinking tag before JSON list
UNCLOSED_THINKING_JSON_LIST = '''<think>
This thought never ends...
[
    {"chapter": 1, "title": "The Beginning"},
    {"chapter": 2, "title": "The Middle"}
]
'''

# Markdown code blocks
MARKDOWN_JSON = '''Here is the requested output:
```json
{
    "characters": [
        {"name": "Alice", "role": "Protagonist"}
    ]
}
```
'''

# Missing closing brace but json_repair might fix it, or we handle it
BROKEN_JSON_TRAILING_COMMA = '''{
    "events": [
        {"title": "Event 1"},
        {"title": "Event 2"},
    ]
}'''

# Smart quotes from the LLM
SMART_QUOTES_JSON = '''{
    "description": "It’s a dark and stormy night."
}'''

PROSE_WITH_THINKING = '''<think>
I should write an action scene.
</think>
The sword swung down, cleaving the air.
'''

PROSE_MARKDOWN = '''```markdown
The wind howled through the empty streets.
```'''
