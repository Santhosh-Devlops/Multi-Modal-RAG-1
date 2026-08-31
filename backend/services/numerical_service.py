import re
from typing import Dict, Any, List

class NumericalService:
    # Common engineering, manufacturing, and scientific units
    UNITS_PATTERN = r"(?:RPM|bar|psi|°C|degrees\s*celsius|K|mm|cm|m|liters\s*/\s*minute|L/min|hours|operating\s*hours|ms|seconds|minutes|kW|MW|V|A|Hz|kHz|kg|g|%|percent|dB|Pa|MPa|kPa|Nm|N\s*m)"

    @classmethod
    def clean_math_to_latex(cls, raw_math: str) -> str:
        """
        Convert raw mathematical notations, symbols, and operators into valid LaTeX math syntax.
        Never invent equations — formats the actual symbols from the source text.
        """
        expr = raw_math.strip()
        if not expr:
            return ""

        # Normalize common math symbols
        expr = expr.replace("×", r"\times ").replace("÷", r"\div ").replace("·", r"\cdot ")
        expr = expr.replace("⩽", r"\le ").replace("⩾", r"\ge ").replace("≤", r"\le ").replace("≥", r"\ge ")
        expr = expr.replace("≪", r"\ll ").replace("≫", r"\gg ").replace("≠", r"\ne ")
        expr = expr.replace("∈", r"\in ").replace("∉", r"\notin ").replace("∝", r"\propto ")
        expr = expr.replace("∑", r"\sum ").replace("∏", r"\prod ").replace("∫", r"\int ")
        expr = expr.replace("∆", r"\Delta ").replace("Δ", r"\Delta ").replace("σ", r"\sigma ").replace("λ", r"\lambda ")
        expr = expr.replace("µ", r"\mu ").replace("ρ", r"\rho ").replace("β", r"\beta ").replace("γ", r"\gamma ")
        expr = expr.replace("∥", r"\lVert ").replace("‖", r"\lVert ")

        # Format fractions like a/b when clean
        expr = re.sub(r'\b([A-Za-z0-9_]+)\s*/\s*([A-Za-z0-9_]+)\b', r'\\frac{\1}{\2}', expr)
        
        # Subscript formatting like H(v) -> H^{(v)}
        expr = re.sub(r'([A-Za-z])\((\w+)\)', r'\1^{(\2)}', expr)

        # Wrap in LaTeX display block
        if not expr.startswith("$$"):
            expr = f"$${expr}$$"
        return expr

    @classmethod
    def extract_numerical_information(
        cls,
        page_text: str,
        page_number: int,
        domain: str = "General"
    ) -> List[Dict[str, Any]]:
        """
        Specialized extractor for:
        1. Dynamic Mathematical Equations & Formula Models (with Equation #, LaTeX syntax, and context)
        2. Numerical quantities, measurements, limits, and tolerances.
        """
        extracted = []
        if not page_text:
            return extracted

        # ==========================================================
        # 1. DYNAMIC SCIENTIFIC & MATHEMATICAL EQUATION PARSER
        # ==========================================================
        
        # Check for explicitly numbered equations, e.g. "(1)", "(2)", "Eq. (3)", "Equation 4"
        eq_patterns = [
            r"(?:(?:Eq\.|Equation)\s*\(?(\d+[a-z]?)\)?|(?:\n|^)\s*\((\d{1,3})\)\s*([^\n]+))",
            r"([A-Za-z_][A-Za-z0-9_\s{}^+\-*/\(\)]*\s*=\s*[^.,;\n]{4,80}\s*(?:\((\d+)\))?)",
            r"(\b(?:min|max|arg\s*min|arg\s*max)\s*[\s\S]*?=\s*[^.,;\n]{4,80}(?:\((\d+)\))?)",
            r"(\b(?:Definition|Theorem|Lemma)\s*\d+[\s\S]*?(?:=|\bin\b|∈)[^.,;\n]{4,80})"
        ]

        for p_idx, pat in enumerate(eq_patterns):
            for match in re.finditer(pat, page_text, re.MULTILINE):
                full_m = match.group(0).strip()
                if len(full_m) < 8 or len(full_m) > 200:
                    continue

                # Find equation number if present
                eq_num = ""
                num_m = re.search(r"\((\d+[a-z]?)\)", full_m)
                if num_m:
                    eq_num = f"Eq. ({num_m.group(1)})"
                elif "Definition" in full_m:
                    d_m = re.search(r"Definition\s*(\d+)", full_m)
                    eq_num = f"Def. {d_m.group(1)}" if d_m else "Definition"
                elif "Theorem" in full_m:
                    t_m = re.search(r"Theorem\s*(\d+)", full_m)
                    eq_num = f"Theorem {t_m.group(1)}" if t_m else "Theorem"
                else:
                    eq_num = f"Eq. (P.{page_number})"

                # Clean math formula
                clean_expr = re.sub(r'^(?:Definition \d+|Theorem \d+|Lemma \d+|where|\.\.\.)\s*[:.]?\s*', '', full_m).strip()
                clean_expr = re.sub(r'\(\d+\)$', '', clean_expr).strip()

                if any(c in clean_expr for c in ["=", "<", ">", r"\min", r"\sum", r"\int", r"\in", r"\lVert", r"\times", r"\Delta", r"\cdot", "+", "-", "/"]):
                    latex_expr = cls.clean_math_to_latex(clean_expr)
                    param_title = f"{eq_num}: {clean_expr.split('=')[0].strip()[:35]}" if "=" in clean_expr else f"{eq_num}: Mathematical Formulation"
                    
                    extracted.append({
                        "page_number": page_number,
                        "parameter_name": param_title,
                        "numerical_value": clean_expr.split("=")[1].strip()[:60] if "=" in clean_expr else "Governing Equation",
                        "unit": "",
                        "category": "Mathematical Equation",
                        "equation_expression": latex_expr,
                        "equation_number": eq_num,
                        "context_sentence": full_m[:250]
                    })

        # ==========================================================
        # 2. NUMERICAL QUANTITIES & MEASUREMENT SPECIFICATIONS
        # ==========================================================
        num_pattern = re.compile(
            rf"([A-Za-z][A-Za-z0-9_\s]{{2,35}}?)\s*[:=–-]?\s*([<>]?\s*[-+]?\d+(?:,\d+)*(?:\.\d+)?(?:\s*[-–]\s*\d+(?:,\d+)*(?:\.\d+)?)?)\s*({cls.UNITS_PATTERN})",
            re.IGNORECASE
        )

        sentences = re.split(r'(?<=[.?!])\s+|\n', page_text)
        for sent in sentences:
            sent_clean = sent.strip()
            if not sent_clean or len(sent_clean) < 10:
                continue

            matches = num_pattern.finditer(sent_clean)
            for m in matches:
                param_raw = m.group(1).strip()
                val_raw = m.group(2).strip()
                unit_raw = m.group(3).strip()

                param_clean = re.sub(r'^(?:the|a|an|and|or|in|at|of|is|are)\s+', '', param_raw, flags=re.IGNORECASE).strip()
                if len(param_clean) < 3 or len(param_clean) > 40:
                    continue

                category = "Measurement"
                if any(w in param_clean.lower() or w in sent_clean.lower() for w in ["limit", "maximum", "max", "critical", "shutdown", "warning", "threshold"]):
                    category = "Operating Limit"
                elif any(w in param_clean.lower() or w in sent_clean.lower() for w in ["tolerance", "runout", "clearance"]):
                    category = "Tolerance Band"
                elif "%" in unit_raw or "percent" in unit_raw.lower():
                    category = "Percentage"
                elif "=" in sent_clean or "equation" in sent_clean.lower() or "formula" in sent_clean.lower():
                    category = "Equation / Calculation"

                equation_expression = f"$${param_clean} = {val_raw}\\text{{ {unit_raw}}}$$"

                extracted.append({
                    "page_number": page_number,
                    "parameter_name": param_clean,
                    "numerical_value": val_raw,
                    "unit": unit_raw,
                    "category": category,
                    "equation_expression": equation_expression,
                    "equation_number": f"P.{page_number}",
                    "context_sentence": sent_clean
                })

        # Deduplicate
        unique_extracted = []
        seen = set()
        for item in extracted:
            key = f"{item['page_number']}_{item['parameter_name'].lower()}_{item['numerical_value']}"
            if key not in seen:
                seen.add(key)
                unique_extracted.append(item)

        return unique_extracted

    @staticmethod
    def numerical_to_searchable_chunks(
        numerical_items: List[Dict[str, Any]],
        doc_id: int,
        domain: str = "General"
    ) -> List[Dict[str, Any]]:
        """
        Package numerical items into structured searchable chunks grouped by page.
        """
        if not numerical_items:
            return []

        chunks = []
        pages_dict = {}
        for item in numerical_items:
            p = item.get("page_number", 1)
            pages_dict.setdefault(p, []).append(item)

        for p_num, items in pages_dict.items():
            lines = [f"• [{it.get('equation_number', 'Param')}] {it['parameter_name']}: {it['numerical_value']} {it['unit']} -> {it['context_sentence']}" for it in items]
            content_text = (
                f"[NUMERICAL SPECIFICATIONS & EQUATIONS: PAGE {p_num}]\n"
                + "\n".join(lines)
            )
            chunks.append({
                "document_id": doc_id,
                "page_number": p_num,
                "chunk_index": 0,
                "content_type": "numerical",
                "content_text": content_text,
                "token_count": len(content_text.split()),
                "domain": domain,
                "metadata_json": "{}"
            })

        return chunks
