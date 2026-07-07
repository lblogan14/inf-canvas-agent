"""Shared prompt helpers (equipment catalog) used by every agent's prompts."""

from inf_canvas.schema.equipment import EQUIPMENT_METADATA, EQUIPMENT_TYPES


def equipment_catalog() -> str:
    """A compact catalog of valid equipment types for the model."""
    return "\n".join(f"- {t}: {EQUIPMENT_METADATA[t].label}" for t in EQUIPMENT_TYPES)
