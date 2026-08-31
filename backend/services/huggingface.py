import base64
import os
from typing import Any

import httpx


HF_URL = "https://router.huggingface.co/v1/chat/completions"
DEFAULT_MODEL = "Qwen/Qwen2.5-VL-7B-Instruct"
MODEL_BY_KIND = {
    "text": "Qwen/Qwen2.5-VL-7B-Instruct",
    "images": "Qwen/Qwen2.5-VL-7B-Instruct",
    "graphs": "Qwen/Qwen2.5-VL-7B-Instruct",
    "tables": "Qwen/Qwen2.5-VL-7B-Instruct",
    "numericals": "Qwen/Qwen2.5-VL-7B-Instruct",
    "equations": "Qwen/Qwen2.5-VL-7B-Instruct",
    "qa": "Qwen/Qwen2.5-VL-7B-Instruct",
}


async def infer_text(prompt: str, model: str = DEFAULT_MODEL) -> str | None:
    """Call HF only when configured; callers retain a deterministic grounded fallback."""
    token = os.environ.get("HUGGINGFACE_TOKEN", "").strip()
    if not token:
        return None
    payload: dict[str, Any] = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "Answer only from the supplied document evidence. Never invent facts or page numbers.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0,
        "max_tokens": 700,
    }
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(75, connect=10)) as client:
            response = await client.post(HF_URL, headers=headers, json=payload)
        if response.status_code >= 400:
            return None
        data = response.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content")
        return content.strip() if isinstance(content, str) and content.strip() else None
    except (httpx.HTTPError, ValueError, KeyError, IndexError, TypeError):
        return None


async def infer_image(image_bytes: bytes, prompt: str, model: str = DEFAULT_MODEL) -> str | None:
    """Optional visual inference helper; the token never crosses into the browser."""
    token = os.environ.get("HUGGINGFACE_TOKEN", "").strip()
    if not token:
        return None
    data_url = "data:image/jpeg;base64," + base64.b64encode(image_bytes).decode("ascii")
    payload: dict[str, Any] = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            }
        ],
        "temperature": 0,
        "max_tokens": 500,
    }
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(75, connect=10)) as client:
            response = await client.post(
                HF_URL,
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json=payload,
            )
        if response.status_code >= 400:
            return None
        content = response.json().get("choices", [{}])[0].get("message", {}).get("content")
        return content.strip() if isinstance(content, str) and content.strip() else None
    except (httpx.HTTPError, ValueError, KeyError, IndexError, TypeError):
        return None
