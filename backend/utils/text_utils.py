import re
from typing import List

def clean_text(text: str) -> str:
    """Clean and normalize whitespace and special unicode characters."""
    if not text:
        return ""
    # Replace multiple newlines with at most two
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Replace multiple spaces with a single space
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

def estimate_tokens(text: str) -> int:
    """Estimate token count based on standard English 4-char per token rule."""
    if not text:
        return 0
    words = len(text.split())
    chars = len(text)
    return max(words, int(chars / 4))

def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """Extract significant keywords from text removing common stopwords."""
    stopwords = {
        "a", "an", "the", "in", "on", "at", "to", "for", "of", "and", "or",
        "is", "are", "was", "were", "it", "this", "that", "with", "as", "by",
        "from", "be", "have", "has", "had", "not", "but", "what", "which",
        "who", "when", "where", "why", "how", "all", "any", "both", "each",
        "few", "more", "most", "other", "some", "such", "no", "nor", "too",
        "very", "can", "will", "just", "should", "now"
    }
    words = re.findall(r'\b[A-Za-z0-9_-]{3,}\b', text.lower())
    filtered = [w for w in words if w not in stopwords and not w.isdigit()]
    
    # Calculate simple frequency
    freq = {}
    for w in filtered:
        freq[w] = freq.get(w, 0) + 1
    
    sorted_keywords = sorted(freq.keys(), key=lambda x: freq[x], reverse=True)
    return sorted_keywords[:max_keywords]

def highlight_snippets(text: str, query: str, max_chars: int = 300) -> str:
    """Generate a clean highlighted context snippet around query terms."""
    if not text:
        return ""
    query_terms = [re.escape(w) for w in extract_keywords(query, 5)]
    if not query_terms:
        return text[:max_chars] + "..." if len(text) > max_chars else text
    
    pattern = "|".join(query_terms)
    match = re.search(pattern, text, re.IGNORECASE)
    if not match:
        return text[:max_chars] + "..." if len(text) > max_chars else text
    
    start_pos = max(0, match.start() - 100)
    end_pos = min(len(text), start_pos + max_chars)
    snippet = text[start_pos:end_pos].strip()
    
    if start_pos > 0:
        snippet = "..." + snippet
    if end_pos < len(text):
        snippet = snippet + "..."
    return snippet
