from typing import Tuple, Optional
import cv2
import numpy as np

from app.utils.logger import log

async def detect_document_contour(
    image: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    edged = cv2.Canny(blurred, 75, 200)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    edged = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)
    # cv2.imshow("img", edged)

    contours, _ = cv2.findContours(
        edged,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    log.info(f"Found {len(contours)} contours")

    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    if not contours:
        quad = await fallback_quad(image)
        overlay = image.copy()
        cv2.polylines(
            overlay,
            [quad],
            isClosed=True,
            color=(0, 255, 0),
            thickness=2
        )
        return quad, overlay

    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    for cnt in contours:
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)

        if len(approx) != 4:
            # log.info(f"Contour rejected: not a quadrilateral (len={len(approx)})")
            continue

        quad = approx.reshape(4, 2)

        overlay = image.copy()
        cv2.polylines(
            overlay,
            [quad.astype(np.int32)],
            isClosed=True,
            color=(0, 255, 0),
            thickness=2
        )

        return quad, overlay

    log.warning("No valid document contour found, using fallback full-image quad")
    quad = await fallback_quad(image)

    overlay = image.copy()
    cv2.polylines(
        overlay,
        [quad],
        isClosed=True,
        color=(0, 255, 0),
        thickness=2
    )

    return quad, overlay

async def draw_document_quad(image: np.ndarray, quad: np.ndarray):
    output = image.copy()
    cv2.polylines(output, [quad.astype(np.int32)], True, (0, 255, 0), 3)
    return output

async def fallback_quad(image: np.ndarray, margin: int = 10) -> np.ndarray:
    h, w = image.shape[:2]
    return np.array(
        [
            [margin, margin],
            [w - margin, margin],
            [w - margin, h - margin],
            [margin, h - margin],
        ],
        dtype=np.int32,
    )