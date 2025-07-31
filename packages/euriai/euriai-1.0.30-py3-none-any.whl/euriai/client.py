import requests
from typing import Optional, Dict, Any

class EuriaiClient:
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4.1-nano",
        endpoint: str = "https://api.euron.one/api/v1/euri/chat/completions"
    ):
        """
        Initializes the EuriaiClient.

        Args:
            api_key (str): Your EURI API key.
            model (str, optional): Model ID to use (e.g., 'gpt-4.1-nano', 'gemini-2.5-flash').
            endpoint (str, optional): API endpoint URL.
        """
        self.api_key = api_key
        self.model = model
        self.endpoint = endpoint

    def generate_completion(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 500,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[list[str]] = None,
    ) -> Dict[str, Any]:
        """
        Generates a non-streamed completion from the model.

        Args:
            prompt (str): The user's prompt to send to the model.
            temperature (float, optional): Sampling temperature (0.2–1.0). Defaults to 0.7.
            max_tokens (int, optional): Maximum number of output tokens. Defaults to 500.
            top_p (float, optional): Nucleus sampling value.
            frequency_penalty (float, optional): Penalizes repetition.
            presence_penalty (float, optional): Encourages new topic generation.
            stop (list of str, optional): Stop sequences to end generation.

        Returns:
            dict: JSON response from the API.
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if top_p is not None:
            payload["top_p"] = top_p
        if frequency_penalty is not None:
            payload["frequency_penalty"] = frequency_penalty
        if presence_penalty is not None:
            payload["presence_penalty"] = presence_penalty
        if stop is not None:
            payload["stop"] = stop

        response = requests.post(self.endpoint, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()

    def stream_completion(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 500,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[list[str]] = None,
    ):
        """
        Streams a response token-by-token (if the model supports streaming).

        Yields:
            str: Each chunk of the streamed output.
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True
        }

        if top_p is not None:
            payload["top_p"] = top_p
        if frequency_penalty is not None:
            payload["frequency_penalty"] = frequency_penalty
        if presence_penalty is not None:
            payload["presence_penalty"] = presence_penalty
        if stop is not None:
            payload["stop"] = stop

        with requests.post(self.endpoint, headers=headers, json=payload, stream=True) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    yield line.decode("utf-8")
