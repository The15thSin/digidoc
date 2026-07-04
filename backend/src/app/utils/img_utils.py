import base64
import cv2
import numpy as np

async def base64_to_ndarray(base64_str: str) -> np.ndarray:
    # Remove data URI prefix if present
    if "," in base64_str:
        base64_str = base64_str.split(",", 1)[1]

    try:
        img_bytes = base64.b64decode(base64_str)
        img_array = np.frombuffer(img_bytes, dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("OpenCV failed to decode image")

        return img
    except Exception as e:
        raise ValueError("Invalid base64 image data") from e

async def ndarray_to_base64(
    image: np.ndarray,
    ext: str = ".png",
    include_data_uri: bool = False
) -> str:
    success, buffer = cv2.imencode(ext, image)
    if not success:
        raise ValueError("Failed to encode image")

    b64_str = base64.b64encode(buffer).decode("utf-8")

    if include_data_uri:
        mime = "png" if ext == ".png" else "jpeg"
        return f"data:image/{mime};base64,{b64_str}"

    return b64_str