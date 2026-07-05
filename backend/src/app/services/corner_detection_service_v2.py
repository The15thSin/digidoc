from cv2.typing import MatLike
from typing import Tuple, Optional, cast, List
from numpy._typing import NDArray
import cv2
import numpy as np

def sample_background_color(image: NDArray[np.uint8], strip: int=10) -> Tuple[int, int, int]:
    h, w = image.shape[:2]
    top = image[0:strip, :, :].reshape(-1, 3)
    bottom = image[h - strip:h, :, :].reshape(-1, 3)
    left = image[:, 0:strip, :].reshape(-1, 3)
    right = image[:, w - strip:w, :].reshape(-1, 3)
    border_pixels = np.vstack([top, bottom, left, right])
    median_color = np.median(border_pixels, axis=0)
    return cast(Tuple[int, int, int], tuple(int(c) for c in median_color))


# ---- 2. Core pipeline --------------------------------------------------------
def pad_image(image: NDArray[np.uint8], pad: int=25, color: Tuple[int, int, int]=(255, 255, 255)) -> MatLike:
    return cv2.copyMakeBorder(
        image, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=color
    )


def remove_small_contours(edged: MatLike, min_length: int=200) -> MatLike:
    contours, _ = cv2.findContours(
        edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
    )

    cleaned = np.zeros_like(edged)

    for cnt in contours:
        perimeter = cv2.arcLength(cnt, closed=False)
        if perimeter >= min_length:
            cv2.drawContours(cleaned, [cnt], -1, 255, thickness=1)

    return cleaned


def get_edges(image: MatLike, canny_low: int=75, canny_high: int=200, blur_ksize: int=5, close_iter: int=2) -> MatLike:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (blur_ksize, blur_ksize), 0)
    edged = cv2.Canny(blurred, canny_low, canny_high)
    edged = remove_small_contours(edged, min_length=300)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    edged = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel, iterations=close_iter)
    edged = cv2.dilate(edged, kernel, iterations=1)

    return edged


def order_points(pts: NDArray[np.float32]):
    pts = pts.reshape(4, 2).astype("float32")
    rect = np.zeros((4, 2), dtype="float32")

    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]   # top-left has smallest sum
    rect[2] = pts[np.argmax(s)]   # bottom-right has largest sum

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]  # top-right has smallest difference
    rect[3] = pts[np.argmax(diff)]  # bottom-left has largest difference

    return rect


def find_document_quadrilateral(image: MatLike, edged: MatLike, max_area_ratio: float=0.97, debug: bool=False):
    height, width = image.shape[:2]
    image_area = height * width

    contours, _ = cv2.findContours(edged, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

    if debug:
        dbg = image.copy()
        cv2.drawContours(dbg, contours, -1, (0, 255, 0), 2)

    for c in contours:
        area = cv2.contourArea(c)
        if area > max_area_ratio * image_area:
            continue  # suspiciously = the whole canvas

        hull = cv2.convexHull(c)
        peri = cv2.arcLength(hull, True)

        for eps_frac in np.arange(0.005, 0.05, 0.002):
            approx = cv2.approxPolyDP(hull, eps_frac * peri, True)
            if len(approx) == 4 and cv2.isContourConvex(approx):
                if debug:
                    print(f"Matched quad at epsilon fraction={eps_frac:.3f}, area={area:.0f}")
                return approx.reshape(4, 2), contours

    return None, contours


def fallback_min_area_rect(contours: List[MatLike]) -> Optional[NDArray[np.float32]]:
    if not contours:
        return None
    c = contours[0]
    rect = cv2.minAreaRect(c)
    box = cv2.boxPoints(rect)
    return box.astype("float32")

def scan_document(image: NDArray[np.uint8], pad: int=25, pad_color: Optional[Tuple[int, int, int]]=None, debug: bool=False) -> Tuple[NDArray[np.float32], str]:
    if pad_color is None:
        pad_color = sample_background_color(image)
        if debug:
            print(f"Auto-sampled background/pad color (BGR): {pad_color}")

    padded = pad_image(image, pad=pad, color=pad_color)
    edged = get_edges(padded)

    if debug:
        print("Canny + dilate result (on padded image):")

    quad, contours = find_document_quadrilateral(padded, edged, debug=debug)

    if quad is not None:
        corners = quad
        method = "approxPolyDP (4-point contour)"
    else:
        corners = fallback_min_area_rect(contours)
        method = "minAreaRect (fallback)"
        if corners is None:
            raise RuntimeError("No contours found at all -- check your Canny thresholds.")

    # Shift corners back into the coordinate space of the original image
    corners = corners.astype("float32") - np.array([pad, pad], dtype="float32")
    # Clip in case padding/rounding pushed a point slightly outside the original frame
    h, w = image.shape[:2]
    corners[:, 0] = np.clip(corners[:, 0], 0, w - 1)
    corners[:, 1] = np.clip(corners[:, 1], 0, h - 1)

    return corners, method