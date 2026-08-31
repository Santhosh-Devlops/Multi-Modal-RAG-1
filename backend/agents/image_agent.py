import time
from typing import Dict, Any
from sqlalchemy.orm import Session
from models.agent_model import AgentActivityLog
from services.image_service import ImageService

class ImageUnderstandingAgent:
    name = "Image Understanding Agent"
    key = "image_agent"
    role_description = "Inspects extracted raster images & diagrams, detects visual schematics/charts/equipment, and produces semantic visual descriptions."
    input_type = "Raster Image Files / PDF Figures"
    output_type = "Visual Metadata & Descriptions"

    @classmethod
    def analyze_image(cls, db: Session, image_path: str, context_text: str, domain: str, trace_id: str) -> Dict[str, Any]:
        start_time = time.time()
        result = ImageService.generate_image_description(image_path, context_text, domain)
        elapsed_ms = (time.time() - start_time) * 1000

        if trace_id:
            log = AgentActivityLog(
                trace_id=trace_id,
                agent_name=cls.name,
                action="Visual Feature Analysis & Captioning",
                input_summary=f"Path: {image_path}, Domain: {domain}",
                output_summary=f"Type: {result['image_type']}, Caption: {result['description'][:100]}...",
                execution_time_ms=elapsed_ms,
                status="Success"
            )
            db.add(log)
            db.commit()

        return result
