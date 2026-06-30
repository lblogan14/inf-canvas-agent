"""Shared FastAPI dependencies."""

from fastapi import Request

from ..canvas.command_bus import CommandBus
from ..canvas.store import CanvasRepository


def get_bus(request: Request) -> CommandBus:
    bus: CommandBus = request.app.state.bus
    return bus


def get_repo(request: Request) -> CanvasRepository:
    repo: CanvasRepository = request.app.state.repo
    return repo
