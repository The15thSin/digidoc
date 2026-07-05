from app.utils.img_utils import base64_to_ndarray
from app.services.corner_detection_service_v1 import detect_document_contour
from fastapi import status, HTTPException
import base64

from app.models.response_models import ScanResponse
from app.services.img_scan_service import convert_base64_image_to_pdf
from app.utils.logger import log

async def handle_scan_image(doc_name: str, image_data: str, scan_mode: str)-> ScanResponse:
    try:
        pdf_buffer = await convert_base64_image_to_pdf(image_data)

        if hasattr(pdf_buffer, "getvalue"):
            pdf_bytes = pdf_buffer.getvalue()
        else:
            pdf_bytes = pdf_buffer

        pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")
        
        return ScanResponse(
            doc_name = doc_name,
            pdf_base64 = pdf_base64
        )

    except ValueError as e:
        log.warning(f"Invalid input: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid input : " + str(e)
        )

    except Exception as e:
        log.error(f"PDF conversion failed : {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to convert image to PDF : {e}"
        )

async def handle_corner_detection(image_data: str):
    try:
        image_ndarray = await base64_to_ndarray(image_data)
        result = await detect_document_contour(image_ndarray)

        quad = result

        corners = quad.astype(float).tolist()

        return {
            "corners": corners
        }

    except ValueError as e:
        log.warning(f"Invalid input: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid input : " + str(e)
        )

    except Exception as e:
        log.error(f"Corner detection failed : {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to detect corners in the image : {e}"
        )