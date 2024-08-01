import json
from typing import Any


def response_to_dict(response_content: str) -> dict[str, Any]:
    """Converts a JSON-encoded response content into a dictionary.

    Args:
        response_content (str): The JSON-encoded response content.

    Returns:
        dict[str, any]: The dictionary representation of the response content.

    Raises:
        json.JSONDecodeError: If the response content is not valid JSON.

    Example:
        response_content = '{"key": "value"}'
        response_dict = response_to_dict(response_content)
        # Output: {'key': 'value'}
    """
    return json.loads(response_content)
