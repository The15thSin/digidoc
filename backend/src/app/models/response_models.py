from typing import List
from pydantic import BaseModel, Field

class ScanResponse(BaseModel):
    doc_name: str
    pdf_base64: str = Field(..., description="The base64 encoded output pdf string")

class CornerResponse(BaseModel):
    corners: List[List[int]] = Field(..., description="List of detected corners in the image")
    overlay_img_base64: str = Field(..., description="The base64 encoded image string with detected corners overlayed")