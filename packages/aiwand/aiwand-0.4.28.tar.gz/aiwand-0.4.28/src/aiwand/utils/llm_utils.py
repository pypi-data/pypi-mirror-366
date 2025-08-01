from typing import Dict, Any, List, Optional

def get_system_msg(messages: List[Dict[str, Any]]) -> Optional[str]:
    """
    Get the system message for the Gemini API.
    """
    for message in messages:
        if message.get("role") == "system":
            return message.get("content", "")
    return None
