from io import BytesIO

from PIL import Image, ImageDraw

from inf_canvas.ai.agents.shared.lines import propose_connections

W, H = 400, 200


def _png_two_boxes_one_line() -> bytes:
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    d.rectangle([40, 80, 90, 120], outline="black", width=3)  # box A (left)
    d.rectangle([310, 80, 360, 120], outline="black", width=3)  # box B (right)
    d.line([90, 100, 310, 100], fill="black", width=3)  # pipe A->B
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _norm_boxes() -> list[tuple[str, float, float, float, float]]:
    return [
        ("A", 40 / W, 80 / H, 90 / W, 120 / H),
        ("B", 310 / W, 80 / H, 360 / W, 120 / H),
    ]


def test_line_hybrid_finds_point_to_point_connection():
    pairs = propose_connections(_png_two_boxes_one_line(), _norm_boxes())
    assert ("A", "B") in pairs  # left-to-right ordering


def test_line_hybrid_no_line_no_connection():
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    d.rectangle([40, 80, 90, 120], outline="black", width=3)
    d.rectangle([310, 80, 360, 120], outline="black", width=3)
    buf = BytesIO()
    img.save(buf, format="PNG")
    assert propose_connections(buf.getvalue(), _norm_boxes()) == []
