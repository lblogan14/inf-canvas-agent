from io import BytesIO

from PIL import Image

from inf_canvas.ai.agents.shared.tiling import make_tiles

W, H = 800, 400


def _png() -> bytes:
    buf = BytesIO()
    Image.new("RGB", (W, H), "white").save(buf, format="PNG")
    return buf.getvalue()


def test_make_tiles_grid_count():
    tiles = make_tiles(_png(), cols=3, rows=2)
    assert len(tiles) == 6


def test_make_tiles_offsets_and_overlap():
    tiles = make_tiles(_png(), cols=2, rows=2, overlap=0.1)
    # First tile is anchored at the top-left corner...
    first = tiles[0]
    assert first.x == 0.0 and first.y == 0.0
    # ...and overlap makes each tile wider than a bare half.
    assert first.w > 0.5
    # Every tile stays within the image bounds.
    for t in tiles:
        assert 0.0 <= t.x <= 1.0
        assert 0.0 <= t.y <= 1.0
        assert t.x + t.w <= 1.0 + 1e-6
        assert t.y + t.h <= 1.0 + 1e-6
        # Each crop is a decodable PNG of nonzero size.
        assert Image.open(BytesIO(t.image)).size[0] > 0


def test_make_tiles_single_tile_is_full_image():
    tiles = make_tiles(_png(), cols=1, rows=1)
    assert len(tiles) == 1
    t = tiles[0]
    assert (t.x, t.y, round(t.w), round(t.h)) == (0.0, 0.0, 1, 1)
