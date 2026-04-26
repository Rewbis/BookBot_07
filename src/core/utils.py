"""
Common utilities for BookBot_07.
"""

import json
import re
from typing import Dict, Any, List, Union

def clean_json_response(content: str) -> Union[Dict[str, Any], List[Any]]:
    """
    Robustly extracts and parses JSON from an LLM response.
    Handles thinking tags, markdown blocks, and leading/trailing text.
    """
    # 1. Discard everything up to and including the last closing thinking tag
    # Common tags: </think>, </thinking>, </thought>
    closing_tags = ["</think>", "</thinking>", "</thought>"]
    for tag in closing_tags:
        if tag in content:
            content = content.split(tag)[-1].strip()
    
    # Also remove any remaining opening tags just in case
    content = re.sub(r'<think>|<thinking>|<thought>', '', content, flags=re.IGNORECASE)
    
    # 2. Try to find content within markdown code blocks
    json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', content, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
    else:
        # 3. If no markdown block, try to find something that looks like JSON
        # Look for the first '[' or '{' and the last ']' or '}'
        json_match = re.search(r'([\[\{].*[\]\}])', content, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = content.strip()

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")
        print(f"Raw string attempted: {json_str[:200]}...")
        return {} if json_str.startswith('{') else []

def clean_prose_response(content: str) -> str:
    """
    Trims all text up to and including the last thinking tag from prose output.
    Also removes any remaining markdown code block markers.
    """
    # 1. Discard everything up to and including the last closing thinking tag
    closing_tags = ["</think>", "</thinking>", "</thought>"]
    for tag in closing_tags:
        if tag in content:
            content = content.split(tag)[-1].strip()
            
    # 2. Remove any remaining opening tags
    content = re.sub(r'<think>|<thinking>|<thought>', '', content, flags=re.IGNORECASE)
    
    # 3. Remove markdown code block markers if the model wrapped the prose
    content = re.sub(r'```(?:markdown)?\s*', '', content)
    content = content.replace('```', '')
    
    return content.strip()

def parse_range_string(range_str: str, max_val: int) -> List[int]:
    """
    Parses a string like '1-5, 8, 10-12' into a list of integers.
    """
    result = set()
    parts = [p.strip() for p in range_str.split(',') if p.strip()]
    for part in parts:
        if '-' in part:
            try:
                start, end = map(int, part.split('-'))
                for i in range(start, end + 1):
                    if 1 <= i <= max_val:
                        result.add(i)
            except ValueError:
                continue
        else:
            try:
                val = int(part)
                if 1 <= val <= max_val:
                    result.add(val)
            except ValueError:
                continue
    return sorted(list(result))
