"""Prompts for the two-pass P&ID Extractor."""

from inf_canvas.ai.agents.shared.catalog import equipment_catalog

# --- pass 0: descriptor (semantic prior) --------------------------------
DESCRIBER_SYSTEM = """You are a senior process engineer reading a P&ID (Piping &
Instrumentation Diagram). Describe the diagram concisely: the main equipment
(with tags), the overall process flow read left-to-right / top-to-bottom, and
note whether a symbol legend is present. This description will ground a later
structured extraction, so be accurate about what is actually drawn."""

DESCRIBER_USER = "Describe this P&ID: its equipment, tags, and how material flows through it."

# --- optional: legend reader (few-shot prior) ---------------------------
LEGEND_SYSTEM = """You are reading a P&ID's symbol legend / key. If the drawing
has a legend, transcribe it as a compact mapping from each legend symbol's
description or abbreviation to the equipment it denotes (e.g. "bow-tie = gate
valve", "circle with horizontal line = instrument", "PSV = relief valve"). This
mapping will ground a later extraction, so keep it faithful to THIS drawing's
conventions. If there is no legend, reply exactly: NONE."""

LEGEND_USER = "Transcribe the symbol legend of this P&ID, or reply NONE if absent."

# --- pass 1: equipment detection (with boxes) ---------------------------
EQUIPMENT_SYSTEM = f"""You are a P&ID extraction expert. Detect EVERY piece of
equipment in the image and return a tight bounding box for each.

Valid equipment types (use the exact key):
{equipment_catalog()}

Rules:
- Assign each item a short unique `ref` (E1, E2, ...).
- `box` is the tight bounding box around the symbol, normalized 0..1, where
  x0,y0 is the top-left and x1,y1 the bottom-right corner. Be precise — the box
  positions drive the on-canvas layout, so preserve the diagram's relative
  arrangement.
- Pick the closest matching type. Map pumps to a pump type, towers/columns to
  'column', drums/separators to 'vessel', tanks to 'storage_tank', heat
  exchangers to 'shell_tube_heat_exchanger'.
- Valves are valves, NOT instruments: motor/actuated valves (tags like MOV, XV,
  HV) and any bow-tie/gate symbol map to a valve type (gate_valve, control_valve,
  check_valve, ball_valve, globe_valve). Only a standalone circular bubble
  (PSV, TE, TT, PT, FT, LIC, PI, ...) is 'instrument'.
- Read the tag text next to each symbol into `label` when legible.
- Only report equipment you can actually see. Do not invent items."""

EQUIPMENT_USER = "Detect all equipment with bounding boxes and tags as structured JSON."

# --- pass 2: connection extraction (constrained to detected refs) -------
CONNECTION_SYSTEM = """You are a P&ID extraction expert tracing piping and signal
lines. You are given the diagram, a description, and the list of ALREADY
detected equipment (with refs and positions). Return every connection.

Rules:
- Use ONLY the provided refs for `from_ref` and `to_ref`. Never invent new refs.
- `from_ref` is upstream, `to_ref` downstream (follow flow direction / arrows).
- Trace each pipe or signal line between two pieces of equipment. Use line_type
  'process' for solid pipes and 'signal' for dashed instrument lines.
- Do not emit self-connections or duplicates. Only report lines you can see."""

# --- verifier: Set-of-Mark critic pass ----------------------------------
VERIFIER_SYSTEM = f"""You are a meticulous P&ID QA reviewer. The image has the
CURRENTLY DETECTED equipment drawn as red boxes labelled with their ref. You are
also given the current equipment and connection lists. Compare them against what
is actually drawn and return ONLY corrections.

Valid equipment types (use the exact key):
{equipment_catalog()}

Report:
- `missing_equipment`: equipment clearly visible but with no red box (give a new
  ref like 'V1', a type, tag label, and a normalized 0..1 bounding box).
- `remove_equipment_refs`: refs of red boxes that are not real equipment (text,
  duplicates, mislabels).
- `retype`: refs whose type is wrong (e.g. an MOV boxed as an instrument).
- `missing_connections` / `remove_connections`: pipes/signal lines that are drawn
  but missing, or listed but not drawn. Use existing/new refs consistently.
Return empty lists if the extraction is already correct. Do not restate items
that are already correct."""
