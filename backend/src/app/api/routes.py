from app.controllers.scan_handlers import handle_scan_image, handle_corner_detection
from app.models.request_models import ScanRequest, CornerRequest
from app.models.response_models import ScanResponse

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def read_root():
    return {"message": "Hello from the routes controller!"}

@router.get("/health")
async def health_check():
    return {"message": "HEALTHY"}

@router.post("/scan", response_model=ScanResponse)
async def scan_image(payload: ScanRequest):
    return await handle_scan_image(payload.doc_name, payload.image_data, payload.scan_mode)

@router.post("/corners")
async def detect_corners(payload: CornerRequest):
    return await handle_corner_detection(payload.image_data)