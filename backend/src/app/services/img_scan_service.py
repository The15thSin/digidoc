import base64
import io
from PIL import Image

from app.utils.logger import log
from app.config import config

local_filepath = "outputs/test.pdf"

async def convert_base64_image_to_pdf(base64_string: str) -> bytes:
    # Clean the base64 string if it contains data URI metadata (e.g., "data:image/png;base64,")
    if "," in base64_string:
        base64_string = base64_string.split(",")[1]

    image_bytes = base64.b64decode(base64_string)
    image = Image.open(io.BytesIO(image_bytes))


    if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
        image = image.convert("RGB")
    elif image.mode != "RGB":
        image = image.convert("RGB")

    log.info("Base64 to Image conversion success...")

    pdf_buffer = io.BytesIO()
    image.save(pdf_buffer, format="PDF")
    if config["IS_DEV"]:
        image.save(local_filepath, format="PDF")
    
    log.info(f"PDF conversion success...")
    return pdf_buffer.getvalue()

