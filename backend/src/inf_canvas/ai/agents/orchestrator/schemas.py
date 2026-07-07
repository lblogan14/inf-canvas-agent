"""Structured-output schema for Optimus routing decisions."""

from typing import Literal

from pydantic import BaseModel


class RouteDecision(BaseModel):
    route: Literal["commander", "answer"]
    rationale: str | None = None
