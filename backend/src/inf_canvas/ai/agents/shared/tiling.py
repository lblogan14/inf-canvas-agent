"""Crop a large drawing into overlapping tiles for dense-sheet extraction.

A single vision call over a 100+ symbol sheet down-samples the image so much
that small symbols vanish. Instead we crop the sheet into an overlapping grid,
detect equipment per tile at full resolution, then the caller remaps each
tile-local box into global 0..1 coordinates and merges the double-counted
boundary symbols with NMS.

Decoupled from the extractor schema — callers work with the `Tile` offsets.
"""

from dataclasses import dataclass
from io import BytesIO

from PIL import Image


@dataclass(frozen=True)
class Tile:
    """One overlapping crop, with its placement in the full image (all 0..1)."""

    image: bytes  # PNG bytes of the crop
    x: float  # normalized left offset within the full image
    y: float  # normalized top offset
    w: float  # normalized width
    h: float  # normalized height


def image_size(image_bytes: bytes) -> tuple[int, int]:
    with Image.open(BytesIO(image_bytes)) as img:
        return img.size


def make_tiles(image_bytes: bytes, cols: int, rows: int, overlap: float = 0.12) -> list[Tile]:
    """Split the image into a ``cols`` x ``rows`` grid of overlapping tiles.

    ``overlap`` is the fraction of a tile added on each side so a symbol sitting
    on a tile boundary still appears whole in at least one tile; the caller
    dedupes the resulting double detections.
    """
    cols = max(1, cols)
    rows = max(1, rows)
    with Image.open(BytesIO(image_bytes)) as im:
        img = im.convert("RGB")
        w, h = img.size
        tw, th = w / cols, h / rows
        ox, oy = tw * overlap, th * overlap
        tiles: list[Tile] = []
        for r in range(rows):
            for c in range(cols):
                x0 = max(0.0, c * tw - ox)
                y0 = max(0.0, r * th - oy)
                x1 = min(float(w), (c + 1) * tw + ox)
                y1 = min(float(h), (r + 1) * th + oy)
                crop = img.crop((int(x0), int(y0), int(x1), int(y1)))
                buf = BytesIO()
                crop.save(buf, format="PNG")
                tiles.append(
                    Tile(
                        image=buf.getvalue(),
                        x=x0 / w,
                        y=y0 / h,
                        w=(x1 - x0) / w,
                        h=(y1 - y0) / h,
                    )
                )
        return tiles
