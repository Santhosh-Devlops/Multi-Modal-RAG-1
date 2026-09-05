from pathlib import Path
from typing import Any, Dict

from PIL import Image

from config import TEXT_GENERATION_MODEL
from services import huggingface as hf_client

CAPTION_PROMPT = (
    "You are a scientific document analyst. Describe this figure precisely and "
    "concisely for someone who cannot see it. Cover: (1) what kind of visual it is "
    "(photo, plot/chart, schematic, architecture diagram, flowchart, screenshot, etc.), "
    "(2) the key elements, axes, labels or components visible, (3) any trend, "
    "relationship or result the figure appears to communicate, and (4) any text, "
    "numbers, units or legend entries you can read in it. "
    "Do not invent details you cannot actually see. Answer in 3-5 sentences, plain text."
)


class ImageService:
    @staticmethod
    def generate_image_description(image_path: str, context_text: str = "", domain: str = "Manufacturing") -> Dict[str, Any]:
        """
        Generate a semantic visual description for an extracted image/figure.

        Uses a vision-language model (via the HF Router chat-completions API,
        see services/huggingface.py) when a token is configured. This is what
        actually lets the chat assistant "understand" figures, charts and
        diagrams instead of just knowing an image exists on some page.

        When no token is configured, this returns an honest, clearly-labeled
        placeholder rather than a fabricated domain-flavoured caption (e.g.
        making up "hydraulic circuit routing" for a random picture) - a
        fabricated caption is worse than no caption because it gets indexed
        and can mislead the chat assistant's answers.
        """
        resolved_path = Path(image_path)
        if not resolved_path.exists():
            return {
                "description": "Image file not found on disk; no visual caption available.",
                "image_type": "Unknown",
                "confidence": 0.0,
            }

        width, height = 0, 0
        image_bytes = b""
        try:
            with Image.open(resolved_path) as img:
                width, height = img.size
                rgb = img.convert("RGB") if img.mode != "RGB" else img
                import io
                buf = io.BytesIO()
                rgb.save(buf, format="PNG")
                image_bytes = buf.getvalue()
        except Exception:
            pass

        if image_bytes and hf_client.is_configured():
            prompt = CAPTION_PROMPT
            if context_text:
                prompt += f"\n\nSurrounding page text for extra context (may or may not relate to this exact figure): {context_text[:400]}"
            caption = hf_client.caption_image(image_bytes, prompt, model=TEXT_GENERATION_MODEL)
            if caption:
                img_type = ImageService._classify_from_caption(caption)
                return {
                    "description": caption,
                    "image_type": img_type,
                    "confidence": 0.93,
                }

        # Honest fallback: no vision model available / call failed.
        aspect_ratio = width / height if height else 1.0
        if aspect_ratio > 1.4:
            shape_hint = "a wide, landscape-oriented figure (often a chart, timeline or wide diagram)"
        elif aspect_ratio < 0.7:
            shape_hint = "a tall, portrait-oriented figure (often a flowchart or stacked diagram)"
        else:
            shape_hint = "a roughly square figure"

        desc = (
            f"Visual captioning is unavailable right now (no vision model configured or the call failed), "
            f"so this is only a placeholder: this is {shape_hint} extracted from the document"
            + (f", located near text about: \"{context_text.split('.')[0].strip()[:140]}\"." if context_text else ".")
            + " Configure HUGGINGFACE_API_TOKEN in the backend .env to get real figure descriptions."
        )
        return {
            "description": desc,
            "image_type": "Figure (uncaptioned)",
            "confidence": 0.3,
        }

    @staticmethod
    def _classify_from_caption(caption: str) -> str:
        c = caption.lower()
        if any(w in c for w in ["line graph", "bar chart", "pie chart", "plot", "histogram", "scatter"]):
            return "Chart / Plot"
        if any(w in c for w in ["flowchart", "flow diagram", "workflow", "pipeline"]):
            return "Flowchart / Pipeline Diagram"
        if any(w in c for w in ["architecture", "block diagram", "system diagram", "framework diagram"]):
            return "Architecture Diagram"
        if any(w in c for w in ["schematic", "circuit", "wiring"]):
            return "Schematic"
        if any(w in c for w in ["screenshot", "interface", "ui"]):
            return "Screenshot"
        if any(w in c for w in ["table"]):
            return "Table Image"
        if any(w in c for w in ["photo", "photograph"]):
            return "Photograph"
        return "Figure / Diagram"
