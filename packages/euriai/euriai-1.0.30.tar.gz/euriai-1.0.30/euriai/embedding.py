import requests
import numpy as np

class EuriaiEmbeddingClient:
    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        self.api_key = api_key
        self.model = model
        self.url = "https://api.euron.one/api/v1/euri/embeddings"

    def embed(self, text: str) -> np.ndarray:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        payload = {
            "input": text,
            "model": self.model
        }

        response = requests.post(self.url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        return np.array(data["data"][0]["embedding"])

    def embed_batch(self, texts: list[str]) -> list[np.ndarray]:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        payload = {
            "input": texts,
            "model": self.model
        }

        response = requests.post(self.url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        return [np.array(obj["embedding"]) for obj in data["data"]]
