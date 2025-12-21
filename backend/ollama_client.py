"""Simple helper for communicating with Ollama REST API to list installed models."""

import requests
from typing import List


def _extract_names_from_response(data) -> List[str]:
    models = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, str):
                models.append(item)
            elif isinstance(item, dict):
                name = item.get("name") or item.get("model") or item.get("id")
                if name:
                    models.append(name)
    elif isinstance(data, dict):
        # Common containers
        for key in ("models", "data", "items"):
            if key in data and isinstance(data[key], list):
                return _extract_names_from_response(data[key])
        # Maybe the dict is a mapping name->info
        for k, v in data.items():
            if isinstance(v, dict) and ("name" in v or "model" in v or "id" in v):
                name = v.get("name") or v.get("model") or v.get("id") or k
                models.append(name)
        # Fallback: treat keys as names
        if not models:
            models = list(data.keys())
    return models


def list_models(base_url: str) -> List[str]:
    """Fetch models from Ollama at `/api/tags` endpoint and return a list of model names.

    Returns an empty list on any error (the caller should handle empty lists gracefully).
    """
    try:
        url = base_url.rstrip("/") + "/api/tags"
        r = requests.get(url, timeout=5)
    except Exception as e:
        print(f"⚠️ Ollama request failed: {e}")
        return []

    if r.status_code != 200:
        print(f"⚠️ Ollama returned status {r.status_code}: {r.text[:400]}")
        return []

    try:
        data = r.json()
    except ValueError:
        print("⚠️ Ollama response not JSON")
        return []

    # Ollama /api/tags returns {"models": [{"name": "...", ...}, ...]}
    models = []
    if isinstance(data, dict) and "models" in data:
        for item in data["models"]:
            if isinstance(item, dict) and "name" in item:
                models.append(item["name"])
    
    # Deduplicate while preserving order
    seen = set()
    dedup = []
    for m in models:
        if m and m not in seen:
            seen.add(m)
            dedup.append(m)
    return dedup

