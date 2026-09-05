"""
Single source of truth for every call this project makes to Hugging Face's
Inference Router. Every other service (model_service, image_service,
embedding_service) imports from here instead of hand-rolling its own
requests call.

Two important lessons learned from real accounts, both handled below:

1. A model existing on the Hub does NOT mean your account can call it via
   the router - it only works if you've enabled a provider (at
   https://huggingface.co/settings/inference-providers) that serves that
   specific model. "not supported by any provider you have enabled" is an
   ACCOUNT SETTING, not a bug - no retry or fallback model list fixes it,
   only enabling providers does.
2. Text-only models must never receive image content, and vision models
   must be tried separately from text models - mixing them into one
   fallback chain wastes API calls/credits and produces confusing 400/405
   errors ("model does not accept image input") on every single request.
   So `chat_complete` takes an explicit `vision=` flag and only ever tries
   the matching chain (TEXT_GENERATION_MODEL+HF_MODEL_FALLBACKS, or
   VISION_MODEL+HF_VISION_FALLBACKS) - never both.
"""
import base64
import logging
from typing import Any, List, Optional

import requests

from config import (
    HUGGINGFACE_API_KEY,
    TEXT_GENERATION_MODEL,
    HF_MODEL_FALLBACKS,
    VISION_MODEL,
    HF_VISION_FALLBACKS,
    HF_REQUEST_TIMEOUT,
)

logger = logging.getLogger("huggingface_client")

CHAT_COMPLETIONS_URL = "https://router.huggingface.co/v1/chat/completions"
# NOTE: HF changed this route's shape - it used to be
# .../hf-inference/pipeline/feature-extraction/{model} (now returns 404/400).
# The current, correct shape nests the task under the model path:
FEATURE_EXTRACTION_URL = "https://router.huggingface.co/hf-inference/models/{model}/pipeline/feature-extraction"


def is_configured() -> bool:
    """True once a Hugging Face token has been supplied via any of the
    supported env var names (see config.py)."""
    return bool(HUGGINGFACE_API_KEY)


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
        "Content-Type": "application/json",
    }


def _models_to_try(preferred: Optional[str], vision: bool) -> List[str]:
    default_model, fallbacks = (VISION_MODEL, HF_VISION_FALLBACKS) if vision else (TEXT_GENERATION_MODEL, HF_MODEL_FALLBACKS)
    ordered = []
    if preferred:
        ordered.append(preferred)
    for m in [default_model, *fallbacks]:
        if m and m not in ordered:
            ordered.append(m)
    return ordered


def chat_complete(
    messages: List[dict],
    model: Optional[str] = None,
    temperature: float = 0.15,
    max_tokens: int = 900,
    vision: bool = False,
) -> Optional[str]:
    """Call the HF Router chat-completions endpoint. `messages` follows the
    standard OpenAI chat format. Tries each model in the matching fallback
    chain (text-only, or vision-only when vision=True - the two chains are
    NEVER mixed) until one succeeds, or returns None if every attempt failed.
    """
    if not is_configured():
        return None

    last_error = None
    permission_or_quota_error = False
    for candidate_model in _models_to_try(model, vision):
        payload: dict[str, Any] = {
            "model": candidate_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        try:
            resp = requests.post(
                CHAT_COMPLETIONS_URL,
                headers=_headers(),
                json=payload,
                timeout=HF_REQUEST_TIMEOUT,
            )
            if resp.status_code == 200:
                data = resp.json()
                content = (
                    data.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content")
                )
                if isinstance(content, str) and content.strip():
                    return content.strip()
                last_error = "empty response content"
                continue

            last_error = f"HTTP {resp.status_code}: {resp.text[:200]}"
            logger.warning("HF chat_complete failed for %s: %s", candidate_model, last_error)

            # 402 (credits exhausted) and 403 (permissions) apply to the whole
            # account, not just this one model - every other model in the
            # chain will fail identically, so stop burning requests/latency.
            if resp.status_code in (402, 403):
                permission_or_quota_error = True
                break
        except requests.RequestException as e:
            last_error = str(e)
            logger.warning("HF chat_complete request error for %s: %s", candidate_model, e)

    if last_error:
        if permission_or_quota_error:
            logger.error(
                "HF chat_complete stopped early (account-level permission/quota issue, "
                "not a per-model problem): %s", last_error
            )
        else:
            logger.error("HF chat_complete exhausted all models. Last error: %s", last_error)
    return None


def caption_image(image_bytes: bytes, prompt: str, model: Optional[str] = None) -> Optional[str]:
    """Vision-language captioning/QA over a single image via the same
    chat-completions endpoint (image_url content part with a base64 data URL).
    Only ever tries vision-capable models (see chat_complete(vision=True)).
    """
    if not is_configured():
        return None
    try:
        data_url = "data:image/png;base64," + base64.b64encode(image_bytes).decode("ascii")
    except Exception:
        return None

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": data_url}},
            ],
        }
    ]
    return chat_complete(messages, model=model, temperature=0.1, max_tokens=350, vision=True)


def get_embedding(text: str, models: List[str]) -> Optional[List[float]]:
    """Dense embedding for a single string via the HF feature-extraction pipeline.
    Tries each candidate model in turn (the free `hf-inference` provider only
    serves a curated, popularity-based list of models for this task, so a
    perfectly valid model name can still 400 with "not supported by provider
    hf-inference" - trying a couple of very popular alternatives in turn
    meaningfully improves the odds one of them is actually deployed there).
    Returns None (never raises) so callers can fall back to a local vector.
    """
    if not is_configured() or not text or not text.strip():
        return None
    clean_text = text.strip()

    for model in models:
        if not model:
            continue
        url = FEATURE_EXTRACTION_URL.format(model=model)
        try:
            resp = requests.post(
                url,
                headers=_headers(),
                json={"inputs": clean_text, "options": {"wait_for_model": True}},
                timeout=min(HF_REQUEST_TIMEOUT, 20),
            )
            if resp.status_code != 200:
                logger.warning("HF embedding failed (%s): HTTP %s: %s", model, resp.status_code, resp.text[:200])
                continue
            data = resp.json()
            # Feature-extraction can return a flat vector, a token-level matrix
            # (needs mean pooling), or a batch of either.
            vec = data
            if isinstance(vec, list) and vec and isinstance(vec[0], list):
                if isinstance(vec[0][0], list):
                    vec = vec[0]  # unwrap batch dimension
                n_tokens = len(vec)
                dim = len(vec[0])
                pooled = [sum(vec[t][d] for t in range(n_tokens)) / n_tokens for d in range(dim)]
                return pooled
            if isinstance(vec, list) and vec and isinstance(vec[0], (int, float)):
                return vec
        except (requests.RequestException, ValueError, KeyError, IndexError, TypeError) as e:
            logger.warning("HF embedding request error for %s: %s", model, e)

    return None
