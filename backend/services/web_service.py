"""
External knowledge layer: lets the chat assistant go beyond the uploaded
document by (a) searching the open web for a handful of relevant pages, and
(b) suggesting relevant open-source models/tools for the paper's topic.

Nothing here requires an API key - it scrapes DuckDuckGo's HTML results
page, which is stable, has no auth, and is fine for a handful of requests
per user question. If a paid search API key (e.g. SERPAPI_KEY / Bing) is
later added, swap `search_web`'s implementation without touching callers.
"""
import logging
import re
from html import unescape
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus, unquote, urlparse, parse_qs

import requests

from config import WEB_SEARCH_ENABLED, WEB_SEARCH_MAX_RESULTS, WEB_SEARCH_TIMEOUT

logger = logging.getLogger("web_service")

DDG_HTML_URL = "https://html.duckduckgo.com/html/"
_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; MultiModalRAG-Assistant/1.0)"}

# Trigger phrases that mean "the user explicitly wants context beyond the document".
EXTERNAL_INFO_TRIGGERS = [
    "recommend", "recommendation", "industry standard", "best practice", "state of the art",
    "state-of-the-art", "sota", "external", "internet", "web", "read more", "further reading",
    "learn more", "latest research", "recent work", "what else should i know", "compare to",
    "related work", "similar papers", "suggest a model", "suggest model", "which model should",
    "which models", "model suggestion", "alternative approach", "current approaches",
]

# Lightweight, keyword -> curated model/tool suggestions. Not exhaustive; meant to
# give the user a genuinely useful starting point rather than a hallucinated list.
MODEL_SUGGESTION_MAP: List[Dict[str, Any]] = [
    {
        "keywords": ["retrieval", "rag", "retrieval-augmented", "embedding", "vector search", "semantic search"],
        "suggestions": [
            "BAAI/bge-large-en-v1.5 or intfloat/e5-large-v2 (strong open embedding models)",
            "Qwen2.5 / Llama-3.1 / Mistral instruct models as the generator LLM",
            "FAISS or Qdrant/Weaviate for the vector index at scale",
        ],
    },
    {
        "keywords": ["image classification", "object detection", "computer vision", "cnn", "convolutional"],
        "suggestions": [
            "timm (PyTorch Image Models) pretrained backbones (ResNet, ConvNeXt, ViT)",
            "YOLOv8/YOLOv10 for real-time object detection",
            "CLIP / OpenCLIP for zero-shot image-text tasks",
        ],
    },
    {
        "keywords": ["caption", "vision-language", "vqa", "visual question", "multimodal"],
        "suggestions": [
            "Qwen2.5-VL or LLaVA-NeXT for open vision-language captioning/VQA",
            "BLIP-2 for lighter-weight image captioning",
        ],
    },
    {
        "keywords": ["time series", "forecasting", "anomaly detection", "sensor data"],
        "suggestions": [
            "Amazon Chronos or Google TimesFM (pretrained time-series foundation models)",
            "Prophet or statsmodels for classical baselines",
            "PyOD for anomaly detection benchmarking",
        ],
    },
    {
        "keywords": ["nlp", "text classification", "sentiment", "named entity", "ner"],
        "suggestions": [
            "DistilBERT / RoBERTa fine-tunes for classification and NER",
            "spaCy for production NER pipelines",
        ],
    },
    {
        "keywords": ["tabular", "structured data", "regression", "classification", "xgboost"],
        "suggestions": [
            "XGBoost or LightGBM for strong tabular baselines",
            "TabPFN for small tabular datasets",
        ],
    },
    {
        "keywords": ["speech", "audio", "asr", "transcription"],
        "suggestions": [
            "OpenAI Whisper (open-source) for speech-to-text",
            "SpeechBrain for custom audio pipelines",
        ],
    },
    {
        "keywords": ["reinforcement learning", "rl", "agent", "policy"],
        "suggestions": [
            "Stable-Baselines3 for standard RL algorithms",
            "Gymnasium for environment interfaces",
        ],
    },
]


def wants_external_info(question: str) -> bool:
    q = question.lower()
    return any(trigger in q for trigger in EXTERNAL_INFO_TRIGGERS)


def search_web(query: str, max_results: int = None) -> List[Dict[str, str]]:
    """Scrape DuckDuckGo's no-JS HTML results page. Returns a list of
    {title, url, snippet}. Returns [] on any failure - callers must treat
    an empty list as 'no external info available right now', never as an error."""
    if not WEB_SEARCH_ENABLED or not query or not query.strip():
        return []

    max_results = max_results or WEB_SEARCH_MAX_RESULTS
    try:
        resp = requests.post(
            DDG_HTML_URL,
            data={"q": query.strip()},
            headers=_HEADERS,
            timeout=WEB_SEARCH_TIMEOUT,
        )
        if resp.status_code != 200:
            logger.warning("web search HTTP %s for query=%r", resp.status_code, query)
            return []
        return _parse_ddg_html(resp.text, max_results)
    except requests.RequestException as e:
        logger.warning("web search request failed for query=%r: %s", query, e)
        return []


def _parse_ddg_html(html: str, max_results: int) -> List[Dict[str, str]]:
    results = []
    # Each result block: <a class="result__a" href="...">Title</a> ... <a class="result__snippet">Snippet</a>
    link_pattern = re.compile(
        r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', re.DOTALL
    )
    snippet_pattern = re.compile(
        r'class="result__snippet"[^>]*>(.*?)</a>', re.DOTALL
    )
    links = link_pattern.findall(html)
    snippets = snippet_pattern.findall(html)

    for i, (raw_url, raw_title) in enumerate(links[:max_results]):
        title = unescape(re.sub(r"<[^>]+>", "", raw_title)).strip()
        url = _clean_ddg_redirect(raw_url)
        snippet = ""
        if i < len(snippets):
            snippet = unescape(re.sub(r"<[^>]+>", "", snippets[i])).strip()
        if title and url:
            results.append({"title": title, "url": url, "snippet": snippet[:280]})

    return results


def _clean_ddg_redirect(href: str) -> str:
    """DuckDuckGo's HTML endpoint wraps result links in a redirect like
    //duckduckgo.com/l/?uddg=<encoded real url>&rut=... - unwrap it."""
    href = unescape(href)
    if href.startswith("//"):
        href = "https:" + href
    parsed = urlparse(href)
    if "duckduckgo.com" in parsed.netloc and parsed.path.startswith("/l/"):
        qs = parse_qs(parsed.query)
        real = qs.get("uddg", [None])[0]
        if real:
            return unquote(real)
    return href


def suggest_related_models(text: str) -> List[str]:
    """Curated, keyword-matched suggestions of open-source models/tools
    relevant to the paper's topic. No network call - static + deterministic."""
    t = text.lower()
    suggestions: List[str] = []
    for entry in MODEL_SUGGESTION_MAP:
        if any(kw in t for kw in entry["keywords"]):
            for s in entry["suggestions"]:
                if s not in suggestions:
                    suggestions.append(s)
    return suggestions[:6]


def build_external_knowledge_block(question: str, domain: str, context_text: str) -> Optional[str]:
    """Build a clearly-separated "beyond your document" markdown block:
    a few real web links plus, when relevant, model/tool suggestions.
    Returns None when there is nothing useful to add (search disabled,
    search failed, and no keyword-matched model suggestions).
    """
    query = question.strip()
    if domain and domain not in ("All", "General"):
        query = f"{query} {domain}"

    results = search_web(query)
    suggestions = suggest_related_models(f"{question} {context_text}")

    if not results and not suggestions:
        return None

    parts = ["**Beyond your document (from the web, not verified against your PDF):**"]

    if results:
        for r in results:
            line = f"- [{r['title']}]({r['url']})"
            if r["snippet"]:
                line += f" — {r['snippet']}"
            parts.append(line)

    if suggestions:
        parts.append("\n**Related open-source models/tools you could try for this topic:**")
        for s in suggestions:
            parts.append(f"- {s}")

    return "\n".join(parts)