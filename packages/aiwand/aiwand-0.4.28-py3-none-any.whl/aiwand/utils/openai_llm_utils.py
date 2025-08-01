from openai import OpenAI
from typing import Dict, Any
from .extras import print_debug_messages, remove_empty_values


def openai_config_params(params: Dict[str, Any]) -> Dict[str, Any]:
    config = {
        "model": params.get("model"),
        "input": params.get("messages"),
        "temperature": params.get("temperature"),
        "top_p": params.get("top_p"),
        "max_output_tokens": params.get("max_completion_tokens"),
        "tools": params.get("tools"),
        "tool_choice": params.get("tool_choice"),
    }
    response_format = params.get("response_format")
    if response_format:
        config["text_format"] = response_format
    return remove_empty_values(config)


def get_openai_response(client: OpenAI, params: Dict[str, Any], debug: bool = False) -> str:
    if debug:
        print_debug_messages(messages=params.get("messages"), params=params)
    response_format = params.get("response_format")
    config = openai_config_params(params)
    if response_format:
        response = client.responses.parse(**config)
        return response.output_parsed
    else:
        response = client.responses.create(**config)
        return response.output_text.strip()
