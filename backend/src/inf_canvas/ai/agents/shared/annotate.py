"""Set-of-Mark overlay: draw the detected boxes + refs onto the image so the
VLM can reason about them by mark when verifying the extraction.

Decoupled from the extractor schema — callers pass `(ref, x0, y0, x1, y1)`
tuples with coordinates normalized 0..1.
"""

from io import BytesIO

from PIL import Image, ImageDraw

Box = tuple[str, float, float, float, float]

_RED = (220, 40, 40)


def annotate_boxes(image_bytes: bytes, boxes: list[Box]) -> bytes:
    """Return a PNG with each box outlined and labelled by its ref."""
    img = Image.open(BytesIO(image_bytes)).convert("RGB")
    w, h = img.size
    draw = ImageDraw.Draw(img)
    for ref, x0, y0, x1, y1 in boxes:
        px0, py0, px1, py1 = x0 * w, y0 * h, x1 * w, y1 * h
        draw.rectangle([px0, py0, px1, py1], outline=_RED, width=2)
        draw.text((px0 + 2, max(0.0, py0 - 11)), ref, fill=_RED)
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
