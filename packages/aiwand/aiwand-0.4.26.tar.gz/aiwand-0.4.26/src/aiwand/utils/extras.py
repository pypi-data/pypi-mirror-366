import json
import pathlib
import mimetypes
import base64
import urllib
import copy
from typing import Any, Dict, List

def convert_to_string(content: Any) -> str:
    """Convert any content to string representation."""
    if isinstance(content, str):
        return content
    elif isinstance(content, (dict, list)):
        try:
            return json.dumps(content, indent=2, ensure_ascii=False)
        except (TypeError, ValueError):
            return str(content)
    else:
        return str(content)
    
def string_to_json(content: str) -> dict:
    """Clean the JSON response from the AI."""
    try:
        cleaned = content.strip("`").split("\n", 1)[1].rsplit("\n", 1)[0]
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return content

def is_url(link: str) -> bool:
    """Check if a link is a URL (starts with http/https)."""
    return link.strip().startswith(('http://', 'https://', 'www.')) 


def image_to_data_url(src: str | pathlib.Path | bytes) -> str:
    if isinstance(src, bytes):
        raw, mime = src, "image/png"
    elif isinstance(src, str) and src.startswith("http"):
        with urllib.request.urlopen(src) as response:
            raw = response.read()
            mime = response.headers.get_content_type()
    else:
        path = pathlib.Path(src).expanduser()
        raw = path.read_bytes()
        mime = mimetypes.guess_type(path.name)[0] or "image/png"
    b64 = base64.b64encode(raw).decode()
    return f"data:{mime};base64,{b64}"


def remove_empty_values(params: Dict[str, Any]) -> Dict[str, Any]:
    """Remove empty values from a dictionary."""
    return {k: v for k, v in params.items() if v is not None}


def print_debug_messages(messages: List[Dict[str, Any]], params: Dict[str, Any]):
    copied_messages = copy.deepcopy(messages)
    for msg in copied_messages:
        msg = copied_messages[-1]
        if msg.get("role") == "user" and msg.get("content"):
            for content in msg["content"]:
                if content.get("type") == "image_url":
                    content["image_url"]["url"] = "<IMAGE_URLs>"
    print(json.dumps(copied_messages, indent=2))
    for k, v in params.items():
        if k != "messages":
            print(f"{k}: {v}\n")
