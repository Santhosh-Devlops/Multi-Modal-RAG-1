from typing import List, Dict, Any
from utils.text_utils import clean_text, estimate_tokens

class ChunkService:
    @staticmethod
    def chunk_document_text(
        pages: List[Dict[str, Any]], 
        doc_id: int, 
        domain: str, 
        target_chunk_words: int = 250, 
        overlap_words: int = 40
    ) -> List[Dict[str, Any]]:
        """
        Split document text into semantic chunks while strictly maintaining page numbers,
        modality, and domain metadata.
        """
        chunks = []
        chunk_idx = 0
        
        for page in pages:
            page_num = page.get("page_number", 1)
            raw_text = clean_text(page.get("page_text", ""))
            if not raw_text:
                continue
                
            paragraphs = [p.strip() for p in raw_text.split("\n\n") if p.strip()]
            current_chunk_words = []
            
            for para in paragraphs:
                para_words = para.split()
                if not para_words:
                    continue
                    
                if len(current_chunk_words) + len(para_words) <= target_chunk_words:
                    current_chunk_words.extend(para_words)
                else:
                    # Save accumulated chunk
                    if current_chunk_words:
                        chunk_text = " ".join(current_chunk_words)
                        chunks.append({
                            "document_id": doc_id,
                            "page_number": page_num,
                            "chunk_index": chunk_idx,
                            "content_type": "text",
                            "content_text": chunk_text,
                            "token_count": estimate_tokens(chunk_text),
                            "domain": domain,
                            "metadata_json": f'{{"page": {page_num}, "type": "text"}}'
                        })
                        chunk_idx += 1
                        # Retain overlap words
                        current_chunk_words = current_chunk_words[-overlap_words:] + para_words
                    else:
                        current_chunk_words = para_words
            
            # Flush any remaining words on this page
            if current_chunk_words:
                chunk_text = " ".join(current_chunk_words)
                chunks.append({
                    "document_id": doc_id,
                    "page_number": page_num,
                    "chunk_index": chunk_idx,
                    "content_type": "text",
                    "content_text": chunk_text,
                    "token_count": estimate_tokens(chunk_text),
                    "domain": domain,
                    "metadata_json": f'{{"page": {page_num}, "type": "text"}}'
                })
                chunk_idx += 1
                
        return chunks

    @staticmethod
    def create_image_chunks(images: List[Dict[str, Any]], doc_id: int, domain: str) -> List[Dict[str, Any]]:
        """Convert extracted visual diagrams into indexed multimodal chunks."""
        chunks = []
        for idx, img in enumerate(images):
            page_num = img.get("page_number", 1)
            desc = img.get("generated_description", "")
            img_type = img.get("image_type", "Diagram")
            img_path = img.get("image_path", "")
            
            chunk_text = f"[VISUAL DIAGRAM PAGE {page_num}] {img_type}: {desc}"
            chunks.append({
                "document_id": doc_id,
                "page_number": page_num,
                "chunk_index": 1000 + idx,
                "content_type": "image",
                "content_text": chunk_text,
                "token_count": estimate_tokens(chunk_text),
                "domain": domain,
                "metadata_json": f'{{"image_path": "{img_path}", "image_type": "{img_type}", "page": {page_num}}}'
            })
        return chunks
