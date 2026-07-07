"""OpenCV line-detection hybrid for connection proposals.

VLMs are strong at recognizing symbols but weaker at tracing every pipe. This
module reads the actual pixels: it isolates the wiring (masking out equipment
symbols), finds connected line components, and proposes a connection when a
single line component clearly bridges exactly two equipment boxes. That's the
unambiguous case; junctions/headers touching 3+ boxes are left to the VLM.

Kept decoupled from the extractor schema: callers pass plain box tuples
`(ref, x0, y0, x1, y1)` with coordinates normalized 0..1.
"""

from collections import defaultdict

import cv2
import numpy as np

Box = tuple[str, float, float, float, float]


def propose_connections(
    image_bytes: bytes,
    boxes: list[Box],
    *,
    ring: int = 10,
    dilate: int = 3,
) -> list[tuple[str, str]]:
    """Return (from_ref, to_ref) pairs for line components joining exactly two
    boxes. Ordering follows left-to-right / top-to-bottom flow. Best-effort:
    returns [] on any decode/analysis issue.
    """
    if len(boxes) < 2:
        return []
    arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return []
    h, w = img.shape

    # Foreground = dark ink (lines + symbols + text) on light background.
    bw = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

    px_boxes: list[tuple[str, int, int, int, int]] = []
    for ref, x0, y0, x1, y1 in boxes:
        ix0, ix1 = sorted((int(x0 * w), int(x1 * w)))
        iy0, iy1 = sorted((int(y0 * h), int(y1 * h)))
        ix0, iy0 = max(0, ix0), max(0, iy0)
        ix1, iy1 = min(w - 1, ix1), min(h - 1, iy1)
        if ix1 <= ix0 or iy1 <= iy0:
            continue
        px_boxes.append((ref, ix0, iy0, ix1, iy1))
        # Erase the symbol so it doesn't merge separate lines into one blob.
        cv2.rectangle(bw, (ix0, iy0), (ix1, iy1), 0, thickness=-1)

    if len(px_boxes) < 2:
        return []

    if dilate > 0:
        bw = cv2.dilate(bw, np.ones((dilate, dilate), np.uint8))

    _, labels = cv2.connectedComponents(bw)

    # For each box, collect the line-component labels touching a thin ring just
    # outside its perimeter (those are the lines leaving the symbol).
    label_refs: dict[int, set[str]] = defaultdict(set)
    centers: dict[str, tuple[float, float]] = {}
    for ref, ix0, iy0, ix1, iy1 in px_boxes:
        centers[ref] = ((ix0 + ix1) / 2, (iy0 + iy1) / 2)
        ex0, ey0 = max(0, ix0 - ring), max(0, iy0 - ring)
        ex1, ey1 = min(w, ix1 + ring), min(h, iy1 + ring)
        ring_mask = np.zeros((h, w), np.uint8)
        cv2.rectangle(ring_mask, (ex0, ey0), (ex1, ey1), 1, thickness=-1)
        cv2.rectangle(ring_mask, (ix0, iy0), (ix1, iy1), 0, thickness=-1)
        for lab in np.unique(labels[ring_mask == 1]):
            if lab != 0:
                label_refs[int(lab)].add(ref)

    pairs: list[tuple[str, str]] = []
    for refs in label_refs.values():
        if len(refs) != 2:
            continue  # dangling (1) or header/junction (3+) -> leave to the VLM
        a, b = sorted(refs, key=lambda r: (centers[r][0], centers[r][1]))
        pairs.append((a, b))

    return list(dict.fromkeys(pairs))
