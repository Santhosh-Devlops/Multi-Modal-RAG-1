import re
import unicodedata
from typing import Dict, Any, List, Optional

class NLPService:
    STOPWORDS = {
        'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'shall', 'should',
        'can', 'could', 'may', 'might', 'must', 'of', 'in', 'on', 'at', 'to', 'for',
        'with', 'about', 'against', 'into', 'through', 'during', 'before', 'after',
        'above', 'below', 'from', 'up', 'down', 'in', 'out', 'over', 'under', 'again',
        'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how',
        'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such',
        'than', 'too', 'very', 'just', 'which', 'who', 'whom', 'this', 'that', 'these', 'those',
        'give', 'show', 'list', 'tell', 'me', 'please', 'done', 'completed'
    }

    # Rich semantic expansion & synonym dictionary across technical and resume domains
    SEMANTIC_EXPANSIONS = {
        "certification": ["certifications", "certificate", "certified", "credentials", "licenses", "coursera", "nptel", "aws", "openai", "courses"],
        "certifications": ["certification", "certificate", "certified", "credentials", "licenses", "coursera", "nptel", "aws", "openai", "courses"],
        "certificate": ["certifications", "certification", "credentials", "licenses"],
        "course": ["certifications", "courses", "training", "credentials"],
        "skill": ["skills", "technical skills", "programming languages", "frameworks", "technologies", "tools", "stack"],
        "skills": ["skill", "technical skills", "programming languages", "frameworks", "technologies", "tools", "stack"],
        "education": ["degree", "b.tech", "btech", "college", "university", "cgpa", "percentage", "hsc", "academic", "school"],
        "college": ["education", "degree", "institution", "university", "mepco"],
        "degree": ["education", "b.tech", "btech", "bachelor", "cgpa"],
        "project": ["projects", "developed", "system", "github", "application", "built"],
        "projects": ["project", "developed", "system", "github", "application", "built"],
        "award": ["awards", "hackathon", "prize", "achievements", "activities", "competitions", "rank"],
        "awards": ["award", "hackathon", "prize", "achievements", "activities", "competitions", "rank"],
        "hackathon": ["awards", "hackathon", "prize", "place", "activities"],
        "experience": ["work experience", "internship", "virtual internship", "role", "employment"],
        "internship": ["virtual internship", "internships", "experience", "role"],
        "contact": ["email", "phone", "linkedin", "github", "address", "location"],
        "speed": ["spindle speed", "rotational velocity", "RPM"],
        "heat": ["temperature", "thermal", "degrees celsius", "°C"],
        "temp": ["temperature", "thermal", "degrees celsius", "°C"],
        "pressure": ["hydraulic pressure", "bar", "psi"],
        "oil": ["lubricant", "lubrication", "ISO VG 46", "bearing grease"],
        "grease": ["bearing grease", "lubrication interval", "guideway lubrication"],
        "formula": ["equation", "mathematical expression", "calculation", "formula"],
        "equation": ["formula", "mathematical expression", "calculation"],
        "calculate": ["formula", "equation", "calculation", "feed rate", "cutting speed", "torque"],
        "tolerance": ["runout tolerance", "clearance", "accuracy", "backlash"],
        "error": ["alarm code", "diagnostic code", "fault code", "troubleshooting"],
        "diagram": ["figure", "schematic", "flowchart", "layout", "architecture"],
        "chart": ["graph", "trend", "distribution", "bar chart", "line graph"],
        "flowchart": ["process flow", "workflow", "sequence", "procedure"],
        "table": ["matrix", "specification table", "parameter table", "ratings"]
    }

    @classmethod
    def normalize_text(cls, text: str) -> str:
        """Unicode normalization, whitespace cleanup."""
        if not text:
            return ""
        norm = unicodedata.normalize("NFKD", text)
        norm = re.sub(r"\s+", " ", norm).strip()
        return norm

    @classmethod
    def tokenize(cls, text: str) -> List[str]:
        """Tokenize string into words, preserving acronyms and numerical codes."""
        norm = cls.normalize_text(text)
        tokens = re.findall(r"\b[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)?\b", norm)
        return tokens

    @classmethod
    def extract_keywords_and_phrases(cls, text: str) -> Dict[str, Any]:
        """
        Extract meaningful multi-word phrases, filtered keywords, and semantic expansions.
        """
        tokens = cls.tokenize(text)
        filtered_keywords = [
            t.lower() for t in tokens
            if t.lower() not in cls.STOPWORDS and len(t) > 1
        ]

        phrases = []
        raw_text_lower = text.lower()
        phrase_patterns = [
            r"\b(?:certifications|certificates|courses|credentials)\s+(?:done|completed|listed|held)\b",
            r"\b(?:technical|programming)\s+(?:skills|languages|tools|stack)\b",
            r"\b(?:academic|educational)\s+(?:background|details|qualifications)\b",
            r"\b[a-z0-9_-]+\s+(?:operating|maintenance|critical|warning|tolerance|hydraulic|spindle|cooling|ambient)\s+[a-z0-9_-]+\b",
            r"\b(?:maximum|minimum|nominal|safe|rated|allowable)\s+[a-z0-9_-]+(?:\s+[a-z0-9_-]+)?\b",
            r"\b[a-z0-9_-]+\s+(?:limit|threshold|temperature|pressure|speed|interval|capacity|rate|specification|diagram|flowchart|table|equation|formula)\b"
        ]
        for pat in phrase_patterns:
            matches = re.findall(pat, raw_text_lower)
            phrases.extend(matches)

        expanded_terms = []
        for kw in filtered_keywords:
            if kw in cls.SEMANTIC_EXPANSIONS:
                expanded_terms.extend(cls.SEMANTIC_EXPANSIONS[kw])

        phrases = list(dict.fromkeys(phrases))[:5]
        all_keywords = list(dict.fromkeys(filtered_keywords + expanded_terms))

        return {
            "tokens": tokens,
            "keywords": all_keywords,
            "phrases": phrases
        }

    @classmethod
    def detect_user_intent(cls, question: str) -> str:
        """
        Classify granular user intent for entity-targeted responses:
        - CERTIFICATIONS: User asking for certifications / courses / credentials
        - SKILLS: User asking for technical skills / languages / tools
        - EDUCATION: User asking for degrees / college / school / CGPA
        - PROJECTS: User asking for projects / GitHub repositories / apps
        - AWARDS: User asking for hackathon awards / prizes / honors
        - INTERNSHIPS: User asking for internships / work experience
        - CONTACT: User asking for email, phone, linkedin, github, address
        - SPINDLE_SPEED: Parameter lookup for spindle speed / RPM
        - TEMPERATURE: Parameter lookup for temperature / thermal limits
        - PRESSURE: Parameter lookup for hydraulic / pneumatic pressure
        - FORMULA_EQUATION: Mathematical formula / equation calculation
        - TABLE_LOOKUP: Tabular specification matrix comparison
        - VISUAL_EXPLANATION: Diagram / flowchart / chart interpretation
        - SUMMARY: General document summary / overview
        - GENERAL_QA: Standard factual QA
        """
        q_lower = question.lower().strip()

        # Document Statistics & Metadata Intents
        if any(w in q_lower for w in ["how many image", "how many picture", "how many figure", "image count", "number of image", "count of image", "images are there", "figures are there"]):
            return "IMAGE_COUNT"
        elif any(w in q_lower for w in ["how many table", "table count", "number of table", "count of table", "tables are there"]):
            return "TABLE_COUNT"
        elif any(w in q_lower for w in ["how many page", "page count", "number of page", "total page", "pages are there", "length of this pdf", "length of this document"]):
            return "PAGE_COUNT"
        elif any(w in q_lower for w in ["how many equation", "how many formula", "equation count", "formula count", "number of equation", "equations are there", "formulas are there"]):
            return "EQUATION_COUNT"

        # Resume & Professional Profile Intents
        if any(w in q_lower for w in ["certification", "certifications", "certificate", "certificates", "courses completed", "credentials", "licenses"]):
            return "CERTIFICATIONS"
        elif any(w in q_lower for w in ["skill", "skills", "technical skills", "programming languages", "technologies", "tech stack", "languages known"]):
            return "SKILLS"
        elif any(w in q_lower for w in ["education", "degree", "college", "university", "cgpa", "percentage", "gpa", "b.tech", "btech", "school", "marks"]):
            return "EDUCATION"
        elif any(w in q_lower for w in ["project", "projects", "what projects", "github repo", "built", "application developed"]):
            return "PROJECTS"
        elif any(w in q_lower for w in ["award", "awards", "hackathon", "prize", "achievements", "activities", "competitions", "rank"]):
            return "AWARDS"
        elif any(w in q_lower for w in ["internship", "internships", "work experience", "experience", "virtual internship"]):
            return "INTERNSHIPS"
        elif any(w in q_lower for w in ["contact", "email", "phone", "mobile", "linkedin", "address", "location"]):
            return "CONTACT"

        # Technical Engineering Intents
        elif any(w in q_lower for w in ["spindle speed", "maximum spindle", "max rpm", "rpm value", "spindle parameter"]):
            return "SPINDLE_SPEED"
        elif any(w in q_lower for w in ["temperature", "temp", "thermal", "degrees celsius", "°c", "heat limit", "critical shutdown temp"]):
            return "TEMPERATURE"
        elif any(w in q_lower for w in ["pressure", "hydraulic pressure", "bar limit", "psi"]):
            return "PRESSURE"
        elif any(w in q_lower for w in ["formula", "equation", "calculate", "how is it calculated", "mathematical expression", "math formula"]):
            return "FORMULA_EQUATION"
        elif any(w in q_lower for w in ["table", "matrix", "row", "column", "compare values", "specifications in table", "parameter table"]):
            return "TABLE_LOOKUP"
        elif any(w in q_lower for w in ["diagram", "image", "figure", "chart", "graph", "schematic", "flowchart", "layout", "visual"]):
            return "VISUAL_EXPLANATION"
        elif any(w in q_lower for w in ["summarize", "summary", "overview", "what is this document", "explain this pdf", "brief outline"]):
            return "SUMMARY"
        elif any(w in q_lower for w in ["how to", "procedure", "steps", "maintenance", "troubleshoot", "instruction"]):
            return "PROCEDURE"
        elif any(w in q_lower for w in ["limit", "maximum", "minimum", "max", "min", "tolerance", "threshold", "operating value"]):
            return "SPECIFIC_PARAMETER"

        return "GENERAL_QA"

    @classmethod
    def extract_named_entities(cls, text: str) -> List[Dict[str, str]]:
        """
        Regex-based Named Entity Recognition (NER).
        """
        entities = []
        meas_matches = re.finditer(r"\b(\d+(?:,\d+)*(?:\.\d+)?\s*(?:RPM|bar|psi|°C|mm|kg|%|hours|kW|V|A))\b", text, re.IGNORECASE)
        for m in meas_matches:
            entities.append({"text": m.group(1), "type": "MEASUREMENT"})

        doc_ref_matches = re.finditer(r"\b((?:page|table|figure|fig|section|chapter)\s*\d+)\b", text, re.IGNORECASE)
        for m in doc_ref_matches:
            entities.append({"text": m.group(1), "type": "DOCUMENT_POINTER"})

        code_matches = re.finditer(r"\b([A-Z]{2,5}[-_][A-Z0-9-_]+)\b", text)
        for m in code_matches:
            entities.append({"text": m.group(1), "type": "MODEL_CODE"})

        return entities

    @classmethod
    def resolve_followup_context(cls, current_query: str, chat_history: List[Dict[str, Any]]) -> str:
        """
        Rewrite follow-up queries that reference previous conversation context.
        """
        if not chat_history:
            return current_query

        q_lower = current_query.lower().strip()
        is_followup = any(q_lower.startswith(prefix) for prefix in [
            "what about", "and for", "how about", "what is its", "what are its", "tell me about that", "explain more", "and the", "what is the"
        ]) and len(current_query.split()) <= 6

        if is_followup:
            last_user_query = ""
            for msg in reversed(chat_history):
                if msg.get("sender") == "user":
                    last_user_query = msg.get("text", "")
                    break

            if last_user_query:
                cleaned_prev = re.sub(r'^(?:what is|what are|tell me about|how to)\s+', '', last_user_query, flags=re.IGNORECASE)
                rewritten = f"{current_query} regarding {cleaned_prev}"
                return rewritten

        return current_query
