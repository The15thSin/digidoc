from typing import List, Optional, Tuple

import cv2
import numpy as np

from app.utils.logger import log


async def detect_document_contour(
    image: np.ndarray,
    min_area_ratio: float = 0.15,
) -> np.ndarray:
    """
    Detect the 4-corner boundary of a document within `image`.

    Handles rotated/skewed pages, low-contrast backgrounds, and slightly
    deformed edges (folded/dog-eared corners) by trying several
    edge-detection strategies and falling back to a rotated
    minimum-area rectangle when no clean quadrilateral contour is found,
    instead of collapsing straight to a full-image box.

    Args:
        image: BGR image (as read by cv2.imread / a decoded upload).
        min_area_ratio: minimum fraction of the frame a candidate
            contour must occupy to be considered the document (guards
            against latching onto small background noise). Lower this
            if your capture flow allows the document to occupy a
            smaller portion of the frame.

    Returns:
        quad: (4, 2) float32 array of corners ordered as
              [top-left, top-right, bottom-right, bottom-left],
              in the coordinate space of the ORIGINAL input image.
    """
    if image is None or image.size == 0:
        raise ValueError("detect_document_contour received an empty image")

    image = _ensure_bgr(image)
    processed, ratio = _resize_for_processing(image)

    try:
        quad = _find_document_quad(processed, min_area_ratio=min_area_ratio)
    except Exception as exc:  # defensive: a bad/unusual frame should degrade, not crash
        log.exception(f"Document contour detection raised an error: {exc}")
        quad = None

    if quad is None:
        log.warning("No document contour found, using fallback full-image quad")
        quad = await fallback_quad(image)
    else:
        quad = order_points(quad / ratio)

    # overlay = await draw_document_quad(image, quad)
    return quad

async def fallback_quad(image: np.ndarray, margin: int = 10) -> np.ndarray:
    """Last-resort quad (whole image minus a small margin) when no
    document boundary can be detected at all."""
    h, w = image.shape[:2]
    return np.array(
        [
            [margin, margin],
            [w - margin, margin],
            [w - margin, h - margin],
            [margin, h - margin],
        ],
        dtype=np.float32,
    )


# ---------------------------------------------------------------------------
# Public utilities (generically useful, e.g. if you later add a perspective
# warp step that consumes this module's output)
# ---------------------------------------------------------------------------


def auto_canny(image: np.ndarray, sigma: float = 0.33) -> np.ndarray:
    """Canny edge detection with thresholds derived from the image's own
    gradient-magnitude distribution, so it adapts to both high- and
    low-contrast photos instead of relying on one fixed pair of
    thresholds. (Deriving thresholds from raw pixel intensity instead of
    gradient strength - a common shortcut - looks reasonable but sets
    the bar far too high on a flat, low-contrast photo, since the
    overall brightness of an image says nothing about how strong its
    edges are.)"""
    gx = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
    gy = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)
    mag = cv2.magnitude(gx, gy)

    high = float(np.percentile(mag, 92))
    low = high * sigma
    return cv2.Canny(image, int(max(0, low)), int(max(low + 1, high)))


def order_points(pts: np.ndarray) -> np.ndarray:
    """
    Orders 4 points as [top-left, top-right, bottom-right, bottom-left].

    approxPolyDP / minAreaRect don't guarantee a consistent winding
    order, and a downstream perspective transform needs source corners
    to correspond correctly to destination corners - this matters most
    exactly when the page is skewed, which is when the "obvious"
    reading order breaks down.

    Note: this is the standard sum/difference heuristic (top-left =
    smallest x+y, bottom-right = largest x+y, top-right = smallest
    x-y, bottom-left = largest x-y). It's reliable for pages skewed or
    rotated up to roughly +/-45 degrees, which covers ordinary
    handheld-photo skew. For a page rotated a full 90 degrees (e.g.
    photographed sideways) it can mislabel which corner is "top" - the
    warp will still be a flat, correctly-proportioned rectangle, just
    not upright. If upright text matters, pair this with a separate
    orientation check after warping.
    """
    pts = pts.astype(np.float32)
    rect = np.zeros((4, 2), dtype=np.float32)

    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    return rect


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _ensure_bgr(image: np.ndarray) -> np.ndarray:
    """Normalizes grayscale or BGRA input to 3-channel BGR. Uploaded
    images don't always arrive as clean 3-channel BGR (grayscale scans,
    PNGs with an alpha channel), and both cv2.cvtColor(..., BGR2GRAY)
    and the green overlay drawing assume it."""
    if image.ndim == 2:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    if image.shape[2] == 4:
        return cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
    return image


def _resize_for_processing(
    image: np.ndarray, target_height: int = 800
) -> Tuple[np.ndarray, float]:
    """Downscale large images to a consistent working height so blur /
    morphology kernel sizes and Canny thresholds behave predictably
    regardless of input resolution. Returns the resized image and the
    scale ratio used, so detected coordinates can be scaled back up."""
    h = image.shape[0]
    ratio = min(1.0, target_height / float(h))
    if ratio == 1.0:
        return image, 1.0
    resized = cv2.resize(image, None, fx=ratio, fy=ratio, interpolation=cv2.INTER_AREA)
    return resized, ratio


def _close_edges(edged: np.ndarray) -> np.ndarray:
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    closed = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel, iterations=2)
    return cv2.dilate(closed, kernel, iterations=1)


def _build_edge_candidates(gray: np.ndarray) -> List[np.ndarray]:
    """Builds several alternative binary edge maps. No single threshold
    or method handles every lighting/contrast/background combination
    a scanned page might show up against, so trying a few cheap
    variants meaningfully improves how often a full boundary loop
    closes cleanly."""
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    candidates = [
        _close_edges(auto_canny(blurred)),  # adapts to gradient strength present in the image
        _close_edges(cv2.Canny(blurred, 75, 200)),  # original fixed thresholds, kept as a second opinion
        _close_edges(
            cv2.adaptiveThreshold(
                blurred,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY_INV,
                21,
                10,
            )
        ),  # helps with uneven lighting / locally textured backgrounds
        _close_edges(
            cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        ),  # catches large, nearly-flat document/background regions whose
        # edge is a small but real step - too weak a gradient for Canny to
        # trust, but a clean global histogram split for Otsu
    ]
    return candidates


def _touches_frame(cnt: np.ndarray, shape: Tuple[int, int], tol: int = 3) -> bool:
    """
    True if cnt's bounding box touches (or nearly touches) all four
    image edges.

    Binary masks (Otsu / adaptive threshold) trace a contour around the
    *background* just as readily as around the document, and when that
    background fills the shot, cv2.findContours happily returns a
    contour that runs along the image border itself - a perfect, huge
    "quadrilateral" that has nothing to do with the actual page. Such
    contours are excluded from consideration entirely rather than
    scored, since a genuine page edge only produces this shape when it
    truly occupies 100% of the frame, in which case there's no boundary
    left in the image to detect anyway and the ordinary fallback is the
    right answer.
    """
    x, y, w, h = cv2.boundingRect(cnt)
    img_h, img_w = shape[:2]
    return x <= tol and y <= tol and x + w >= img_w - tol and y + h >= img_h - tol


def _approximate_quad(cnt: np.ndarray) -> Optional[np.ndarray]:
    """Tries a range of approxPolyDP epsilons against the contour's
    convex hull to coerce it into a clean convex quadrilateral. Using
    the hull (rather than the raw contour) absorbs small notches from
    folded/dog-eared corners or noisy edges. Returns None if nothing in
    the tried range yields a convex 4-point polygon."""
    hull = cv2.convexHull(cnt)
    peri = cv2.arcLength(hull, True)

    for eps_fraction in (0.01, 0.02, 0.03, 0.04, 0.05):
        approx = cv2.approxPolyDP(hull, eps_fraction * peri, True)
        if len(approx) == 4 and cv2.isContourConvex(approx):
            return approx.reshape(4, 2)

    return None


def _find_document_quad(
    image: np.ndarray, min_area_ratio: float = 0.15
) -> Optional[np.ndarray]:
    """
    Searches multiple edge maps for the best 4-point document candidate.

    Falls back to the rotated minimum-area rectangle of the largest
    sufficiently-big contour if nothing produces a clean quadrilateral -
    this keeps skewed pages well-fitted instead of collapsing straight
    to the full-image fallback whenever approxPolyDP can't hit exactly
    4 points (e.g. a corner is slightly rounded, motion-blurred, or in
    shadow).
    """
    image_area = image.shape[0] * image.shape[1]
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    best_quad, best_quad_area = None, 0.0
    best_cnt, best_cnt_area = None, 0.0

    for edged in _build_edge_candidates(gray):
        contours, _ = cv2.findContours(edged, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            continue

        for cnt in sorted(contours, key=cv2.contourArea, reverse=True)[:8]:
            area = cv2.contourArea(cnt)
            if area < min_area_ratio * image_area:
                break  # sorted descending - nothing further qualifies either

            if _touches_frame(cnt, image.shape):
                continue  # likely the background/frame, not the document - keep looking

            if area > best_cnt_area:
                best_cnt, best_cnt_area = cnt, area

            quad = _approximate_quad(cnt)
            if quad is not None and area > best_quad_area:
                best_quad, best_quad_area = quad, area

    if best_quad is not None:
        log.info(f"Document quad found via contour approximation (area={best_quad_area:.0f})")
        return best_quad.astype(np.float32)

    if best_cnt is not None:
        log.info("No clean 4-point contour; using rotated min-area rectangle instead")
        return cv2.boxPoints(cv2.minAreaRect(best_cnt)).astype(np.float32)

    return None