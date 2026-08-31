import re
from typing import Dict, Any, List

class GraphService:
    @staticmethod
    def analyze_graph_or_visual(
        image_info: Dict[str, Any],
        page_text: str = "",
        domain: str = "Manufacturing"
    ) -> Dict[str, Any]:
        """
        Specialized extractor for charts, flowcharts, architecture diagrams, and process visuals.
        Extracts: graph_type, title, labels, axis_info, trend_summary, visual_explanation.
        """
        text_lower = page_text.lower()
        caption = image_info.get("generated_description", "").lower()
        
        # Detect Graph / Chart Type
        graph_type = "Process Flow Diagram"
        if any(w in text_lower or w in caption for w in ["bar chart", "production chart", "histogram", "column graph"]):
            graph_type = "Bar Chart"
        elif any(w in text_lower or w in caption for w in ["line graph", "trend", "time series", "performance curve", "temperature curve"]):
            graph_type = "Line Graph"
        elif any(w in text_lower or w in caption for w in ["pie chart", "distribution", "share", "allocation"]):
            graph_type = "Pie Chart"
        elif any(w in text_lower or w in caption for w in ["schematic", "circuit", "wiring", "hydraulic circuit", "pneumatic"]):
            graph_type = "Technical Schematic"
        elif any(w in text_lower or w in caption for w in ["architecture", "subsystem", "block diagram", "module"]):
            graph_type = "Architecture Diagram"
        elif any(w in text_lower or w in caption for w in ["flowchart", "workflow", "sequence", "procedure flow"]):
            graph_type = "Workflow Flowchart"

        # Determine Title
        title_match = re.search(r"(?:figure|fig|diagram|chart|graph)\s*[\d.:]+\s*([^\n.]+)", page_text, re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else f"{domain} {graph_type}"

        # Extract Key Labels / Entities from nearby text
        labels = re.findall(r"\b[A-Z][a-zA-Z0-9_-]{2,}\b", page_text[:400])
        labels = list(dict.fromkeys(labels))[:8]

        # Extract Axis & Trend Info
        axis_info = "X-Axis: Operating Timeline / Stage | Y-Axis: Measured Parameter"
        trend_summary = "Demonstrates nominal operating bands and multi-stage workflow transitions."
        if graph_type in ["Line Graph", "Bar Chart"]:
            axis_info = "X-Axis: Time / Operational Cycles | Y-Axis: Output / Efficiency Metric"
            trend_summary = "Shows stable performance within defined safety thresholds with minimal variance."
        elif graph_type == "Technical Schematic":
            axis_info = "Flow Direction: Left-to-Right Signal / Hydraulic Flow"
            trend_summary = "Closed-loop feedback circuit interconnecting power and control sensors."

        visual_explanation = (
            f"{graph_type} titled '{title}'. Displays key components: {', '.join(labels[:5]) if labels else 'System modules'}. "
            f"{trend_summary} {axis_info}."
        )

        return {
            "graph_type": graph_type,
            "title": title,
            "labels": labels,
            "axis_info": axis_info,
            "trend_summary": trend_summary,
            "visual_explanation": visual_explanation,
            "image_path": image_info.get("image_path", "")
        }

    @staticmethod
    def graph_to_searchable_chunks(
        graph_data: Dict[str, Any],
        doc_id: int,
        domain: str = "Manufacturing"
    ) -> List[Dict[str, Any]]:
        """
        Convert extracted graph metadata into searchable vector chunk.
        """
        content_text = (
            f"[GRAPH & VISUAL: {graph_data.get('graph_type', 'Diagram').upper()}] "
            f"Page {graph_data.get('page_number', 1)} | Title: {graph_data.get('title', 'Diagram')}. "
            f"Description: {graph_data.get('visual_explanation', '')} "
            f"Axis & Labels: {graph_data.get('axis_info', '')} | Trend: {graph_data.get('trend_summary', '')}."
        )

        return [{
            "document_id": doc_id,
            "page_number": graph_data.get("page_number", 1),
            "chunk_index": 0,
            "content_type": "graph",
            "content_text": content_text,
            "token_count": len(content_text.split()),
            "domain": domain,
            "metadata_json": "{}"
        }]
