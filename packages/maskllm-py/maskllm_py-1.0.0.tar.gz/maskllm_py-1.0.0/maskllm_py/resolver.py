import requests

# === Custom Exceptions ===

class MaskLLMError(Exception):
    """Base class for all MaskLLM SDK errors."""
    pass

class InvalidKeyError(MaskLLMError):
    """Raised when the provided masked key is invalid."""
    pass

class UsageExceededError(MaskLLMError):
    """Raised when usage limits are exceeded."""
    pass

class ThrottledError(MaskLLMError):
    """Raised when too many requests are sent in a short time."""
    pass

class NetworkError(MaskLLMError):
    """Raised when a network-related error occurs."""
    pass

class InvalidResponseError(MaskLLMError):
    """Raised when response is not as expected from the server."""
    pass

# === Utility Methods ===

def resolve_masked_key(masked_key: str) -> str:
    """
    Resolve a masked key to its actual value via the MaskLLM API.

    :param masked_key: The masked API key string.
    :return: The resolved source key as a string.
    :raises MaskLLMError: For various failure reasons.
    """
    if not masked_key:
        raise InvalidKeyError("No key provided.")

    url = "https://api.maskllm.com/resolver/resolve_masked_api_key"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "token": masked_key
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=5)

        if response.status_code == 401:
            raise InvalidKeyError("Invalid masked key.")
        elif response.status_code == 403:
            raise UsageExceededError("Usage limit exceeded.")
        elif response.status_code == 429:
            raise ThrottledError("Too many requests sent. Try again later.")
        elif not response.ok:
            raise NetworkError(f"Unexpected error: {response.status_code} {response.reason}")

        data = response.json()
        if "resolvedKey" not in data:
            raise InvalidResponseError("Missing 'resolvedKey' in response.")

        return data["resolvedKey"]

    except requests.exceptions.RequestException as e:
        raise NetworkError(str(e)) from e
