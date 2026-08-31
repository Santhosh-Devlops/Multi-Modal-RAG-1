from typing import List, Dict, Any
import pandas as pd

class TableService:
    @staticmethod
    def parse_tabular_file(file_path: str, file_type: str) -> Dict[str, Any]:
        """
        Parse standalone CSV or XLSX spreadsheet into structured markdown, JSON, and natural-language representations.
        """
        try:
            if file_type.lower() == "csv":
                df = pd.read_csv(file_path)
            elif file_type.lower() in ["xlsx", "xls"]:
                df = pd.read_excel(file_path)
            else:
                return {"tables": [], "row_count": 0, "column_count": 0}
            
            # Fill NaN values with empty string
            df = df.fillna("")
            headers = [str(c) for c in df.columns.tolist()]
            
            # Build markdown
            separator = ["---"] * len(headers)
            md_lines = [
                "| " + " | ".join(headers) + " |",
                "| " + " | ".join(separator) + " |"
            ]
            
            structured_data = [headers]
            nl_statements = []
            
            for r_idx, row in df.iterrows():
                row_vals = [str(v) for v in row.tolist()]
                structured_data.append(row_vals)
                md_lines.append("| " + " | ".join(row_vals) + " |")
                
                # Create natural language assertion
                pairs = [f"{h}: {v}" for h, v in zip(headers, row_vals) if v]
                if pairs:
                    nl_statements.append(f"Row {r_idx + 1} ({', '.join(pairs)})")
            
            markdown_table = "\n".join(md_lines)
            nl_summary = f"Spreadsheet Dataset ({', '.join(headers[:4])}...):\n" + "\n".join(nl_statements)
            
            return {
                "tables": [{
                    "page_number": 1,
                    "table_index": 1,
                    "raw_markdown": markdown_table,
                    "structured_json": structured_data,
                    "natural_language_text": nl_summary,
                    "row_count": len(df),
                    "column_count": len(headers)
                }],
                "total_rows": len(df),
                "total_cols": len(headers)
            }
        except Exception as e:
            print(f"Error parsing tabular file: {e}")
            return {"tables": [], "total_rows": 0, "total_cols": 0}
            
    @staticmethod
    def table_to_searchable_chunks(table_info: Dict[str, Any], doc_id: int, domain: str) -> List[Dict[str, Any]]:
        """
        Convert table metadata into searchable vector chunk representation.
        """
        nl_text = table_info.get("natural_language_text", "")
        raw_md = table_info.get("raw_markdown", "")
        page_num = table_info.get("page_number", 1)
        
        chunk_text = f"[TABLE PAGE {page_num}]\n{raw_md}\n\nStructured Interpretation:\n{nl_text}"
        
        return [{
            "document_id": doc_id,
            "page_number": page_num,
            "content_type": "table",
            "content_text": chunk_text,
            "domain": domain,
            "metadata_json": f'{{"table_index": {table_info.get("table_index", 1)}, "rows": {table_info.get("row_count", 0)}, "cols": {table_info.get("column_count", 0)}}}'
        }]
