from pydantic import BaseModel, HttpUrl, Field
from typing import Optional

class ScanRequest(BaseModel):
    doc_name: str
    image_data: str = Field(..., description="The base64 encoded image string")
    scan_mode: str

class CornerRequest(BaseModel):
    image_data: str = Field(..., description="The base64 encoded image string")