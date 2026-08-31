import io
import re
from pathlib import Path
from typing import List, Dict, Any
import fitz  # PyMuPDF
import pdfplumber
from PIL import Image

from config import EXTRACTED_IMAGES_DIR, EXTRACTED_TABLES_DIR
from utils.file_utils import render_pdf_page_preview
from utils.text_utils import clean_text

class PDFService:
    @staticmethod
    def extract_pdf_content(pdf_path: str, doc_id: int, doc_domain: str = "General") -> Dict[str, Any]:
        """
        Comprehensive Multimodal PDF Extraction:
        1. Clean plain text with structural headings & word counts
        2. Extracted high-resolution raster & vector images (PIL RGB compositing, zero black-box artifacts)
        3. Extracted tables as BOTH visual image crops AND structured row/column matrices
        4. Extracted diagrams/graphs as visual high-DPI image crops
        5. Page preview thumbnails
        """
        results = {
            "page_count": 0,
            "pages": [],
            "images": [],
            "tables": [],
            "graphs": []
        }
        
        pdf_doc = fitz.open(pdf_path)
        results["page_count"] = len(pdf_doc)
        
        # Step 1: Extract text, raster images, and page preview thumbnails
        for page_idx in range(len(pdf_doc)):
            page_num = page_idx + 1
            page = pdf_doc[page_idx]
            
            # Extract clean plain text
            page_text = clean_text(page.get_text("text"))
            
            # Render page preview thumbnail
            preview_url = render_pdf_page_preview(pdf_path, page_num, doc_id)
            
            # Extract images embedded on this page
            image_list = page.get_images(full=True)
            page_image_count = 0
            
            for img_index, img_info in enumerate(image_list):
                xref = img_info[0]
                try:
                    base_image = pdf_doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    w, h = base_image["width"], base_image["height"]
                    
                    # Filter out tiny icon artifacts
                    if w > 50 and h > 50:
                        image_filename = f"doc_{doc_id}_p{page_num}_img_{img_index + 1}.png"
                        image_filepath = EXTRACTED_IMAGES_DIR / image_filename
                        
                        # Process image through PIL to eliminate CMYK/alpha black box issues
                        raw_img = Image.open(io.BytesIO(image_bytes))
                        if raw_img.mode in ("RGBA", "LA") or (raw_img.mode == "P" and "transparency" in raw_img.info):
                            bg = Image.new("RGB", raw_img.size, (255, 255, 255))
                            if raw_img.mode != "RGBA":
                                raw_img = raw_img.convert("RGBA")
                            bg.paste(raw_img, mask=raw_img.split()[3])
                            clean_img = bg
                        elif raw_img.mode != "RGB":
                            clean_img = raw_img.convert("RGB")
                        else:
                            clean_img = raw_img
                            
                        clean_img.save(str(image_filepath), format="PNG")
                        
                        img_type = "Schematic/Diagram" if (w > 200 and h > 200) else "Technical Illustration"
                        
                        results["images"].append({
                            "page_number": page_num,
                            "image_path": f"/api/static/images/{image_filename}",
                            "local_filepath": str(image_filepath),
                            "image_name": f"Figure/Image (Page {page_num}, #{img_index + 1})",
                            "width": w,
                            "height": h,
                            "image_type": img_type
                        })
                        page_image_count += 1
                except Exception as e:
                    print(f"Notice during image extract xref {xref}: {e}")
            
            # Step 1.2: Check for labeled figures on the page (Fig. 1, Fig. 2, Figure 1) and crop them
            fig_matches = re.finditer(r"\b(?:Fig\.|Figure)\s*(\d+[a-z]?)\b", page_text, re.IGNORECASE)
            for fm in fig_matches:
                fig_label = fm.group(0)
                fig_num = fm.group(1)
                
                # Search location of Figure text
                rects = page.search_for(fig_label)
                if rects:
                    f_rect = rects[0]
                    # Crop above or below caption
                    crop_rect = fitz.Rect(max(0, f_rect.x0 - 150), max(0, f_rect.y0 - 220), min(page.rect.width, f_rect.x1 + 150), min(page.rect.height, f_rect.y1 + 40))
                    if crop_rect.width > 100 and crop_rect.height > 80:
                        try:
                            pix = page.get_pixmap(clip=crop_rect, dpi=180)
                            graph_filename = f"graph_doc_{doc_id}_p{page_num}_fig_{fig_num}.png"
                            graph_filepath = EXTRACTED_IMAGES_DIR / graph_filename
                            pix.save(str(graph_filepath))
                            
                            results["graphs"].append({
                                "page_number": page_num,
                                "title": f"{fig_label} (Page {page_num})",
                                "graph_type": "Schematic / Flow Diagram",
                                "image_path": f"/api/static/images/{graph_filename}",
                                "visual_explanation": f"Rendered diagram and visual schematic corresponding to {fig_label} on Page {page_num}.",
                                "axis_info": "Visual graph coordinate mapping",
                                "trend_summary": "Extracted architectural and process flow diagram."
                            })
                        except Exception as e:
                            print(f"Notice cropping figure {fig_label}: {e}")
            
            results["pages"].append({
                "page_number": page_num,
                "page_text": page_text,
                "image_count": page_image_count,
                "table_count": 0,
                "preview_image_path": preview_url
            })
            
        pdf_doc.close()
        
        # Step 2: Extract tables via pdfplumber and visual bounding box crops
        try:
            with pdfplumber.open(pdf_path) as plumber_pdf:
                for page_idx, plumber_page in enumerate(plumber_pdf.pages):
                    page_num = page_idx + 1
                    extracted_tables = plumber_page.extract_tables()
                    
                    for t_idx, table_data in enumerate(extracted_tables):
                        if not table_data or len(table_data) < 2:
                            continue
                        
                        cleaned_table = []
                        for row in table_data:
                            cleaned_row = [str(cell).strip() if cell is not None else "" for cell in row]
                            if any(cleaned_row):
                                cleaned_table.append(cleaned_row)
                        
                        if len(cleaned_table) < 2:
                            continue
                            
                        headers = cleaned_table[0]
                        separator = ["---"] * len(headers)
                        md_lines = [
                            "| " + " | ".join(headers) + " |",
                            "| " + " | ".join(separator) + " |"
                        ]
                        for row in cleaned_table[1:]:
                            padded_row = row + [""] * (len(headers) - len(row))
                            md_lines.append("| " + " | ".join(padded_row[:len(headers)]) + " |")
                        markdown_table = "\n".join(md_lines)
                        
                        nl_statements = []
                        for r_i, row in enumerate(cleaned_table[1:], start=1):
                            row_pairs = []
                            for c_i, h in enumerate(headers):
                                if c_i < len(row) and row[c_i]:
                                    row_pairs.append(f"{h}: {row[c_i]}")
                            if row_pairs:
                                nl_statements.append(f"Row {r_i} ({', '.join(row_pairs)})")
                                
                        nl_summary = f"Table on page {page_num} ({headers[0]} table):\n" + "\n".join(nl_statements)
                        
                        # Generate cropped image for this table from PDF page
                        table_image_url = ""
                        try:
                            doc_temp = fitz.open(pdf_path)
                            page_temp = doc_temp[page_idx]
                            # Search for table header words
                            search_word = headers[0][:15] if headers else "Table"
                            rects = page_temp.search_for(search_word)
                            t_rect = rects[0] if rects else fitz.Rect(50, 100, page_temp.rect.width - 50, page_temp.rect.height - 100)
                            clip_box = fitz.Rect(max(0, t_rect.x0 - 40), max(0, t_rect.y0 - 20), min(page_temp.rect.width, t_rect.x1 + 350), min(page_temp.rect.height, t_rect.y1 + 250))
                            pix_t = page_temp.get_pixmap(clip=clip_box, dpi=180)
                            t_filename = f"table_doc_{doc_id}_p{page_num}_t{t_idx + 1}.png"
                            pix_t.save(str(EXTRACTED_IMAGES_DIR / t_filename))
                            table_image_url = f"/api/static/images/{t_filename}"
                            doc_temp.close()
                        except Exception:
                            table_image_url = ""

                        results["tables"].append({
                            "page_number": page_num,
                            "table_index": t_idx + 1,
                            "title": f"Table on Page {page_num} ({headers[0] if headers else 'Data Matrix'})",
                            "raw_markdown": markdown_table,
                            "structured_json": cleaned_table,
                            "natural_language_text": nl_summary,
                            "row_count": len(cleaned_table) - 1,
                            "column_count": len(headers),
                            "image_path": table_image_url
                        })
                        
                        if page_idx < len(results["pages"]):
                            results["pages"][page_idx]["table_count"] += 1
        except Exception as e:
            print(f"Table extraction notice: {e}")
            
        # Step 3: Heuristic Table Extraction for borderless / IEEE scientific tables (e.g. TABLE 1, TABLE 2...)
        if len(results["tables"]) == 0:
            for page_dict in results["pages"]:
                p_text = page_dict.get("page_text", "")
                p_num = page_dict.get("page_number", 1)
                
                table_headers_matches = re.finditer(r"\bTABLE\s*(\d+)\s*\n+([^\n]+)", p_text, re.IGNORECASE)
                for tm in table_headers_matches:
                    t_num = tm.group(1)
                    t_title = f"TABLE {t_num}: {tm.group(2).strip()}"
                    
                    # Extract surrounding lines
                    start_pos = tm.end()
                    sub_text = p_text[start_pos:start_pos + 1200]
                    lines = [l.strip() for l in sub_text.split("\n") if len(l.strip()) > 3][:12]
                    
                    if len(lines) >= 3:
                        # Attempt whitespace column split
                        rows_parsed = []
                        for l in lines:
                            cols = re.split(r'\s{2,}|\t|;', l)
                            cols = [c.strip() for c in cols if c.strip()]
                            if len(cols) >= 2:
                                rows_parsed.append(cols)
                                
                        if len(rows_parsed) >= 2:
                            max_cols = max(len(r) for r in rows_parsed)
                            h_cols = rows_parsed[0] + [f"Col_{i+1}" for i in range(len(rows_parsed[0]), max_cols)]
                            
                            md_lines = ["| " + " | ".join(h_cols) + " |", "| " + " | ".join(["---"] * len(h_cols)) + " |"]
                            for r in rows_parsed[1:]:
                                pad_r = r + [""] * (len(h_cols) - len(r))
                                md_lines.append("| " + " | ".join(pad_r[:len(h_cols)]) + " |")
                            
                            # Crop table region
                            t_img_url = ""
                            try:
                                doc_temp = fitz.open(pdf_path)
                                page_temp = doc_temp[p_num - 1]
                                rects = page_temp.search_for(f"TABLE {t_num}")
                                t_rect = rects[0] if rects else fitz.Rect(50, 80, page_temp.rect.width - 50, page_temp.rect.height - 80)
                                clip_box = fitz.Rect(max(0, t_rect.x0 - 40), max(0, t_rect.y0 - 20), min(page_temp.rect.width, t_rect.x1 + 450), min(page_temp.rect.height, t_rect.y1 + 350))
                                pix_t = page_temp.get_pixmap(clip=clip_box, dpi=180)
                                t_filename = f"table_doc_{doc_id}_p{p_num}_t{t_num}.png"
                                pix_t.save(str(EXTRACTED_IMAGES_DIR / t_filename))
                                t_img_url = f"/api/static/images/{t_filename}"
                                doc_temp.close()
                            except Exception:
                                t_img_url = ""

                            results["tables"].append({
                                "page_number": p_num,
                                "table_index": int(t_num),
                                "title": t_title,
                                "raw_markdown": "\n".join(md_lines),
                                "structured_json": [h_cols] + rows_parsed[1:],
                                "natural_language_text": f"{t_title} on Page {p_num} with {len(rows_parsed) - 1} rows.",
                                "row_count": len(rows_parsed) - 1,
                                "column_count": len(h_cols),
                                "image_path": t_img_url
                            })
                            page_dict["table_count"] += 1
                            
        return results
