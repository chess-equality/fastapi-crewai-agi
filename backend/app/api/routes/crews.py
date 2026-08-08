import importlib
from collections.abc import Callable
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.config import settings

router = APIRouter(prefix="/crews", tags=["crews"])


class FlowKickoffRequest(BaseModel):
    inputs: dict = {}


def _discover_flows() -> dict[str, Callable[[dict | None], object]]:
    """Discover all flow packages under app/crews and import their kickoff entry points."""
    crews_dir = Path(__file__).resolve().parents[2] / "crews"
    flows: dict[str, Callable[[dict | None], object]] = {}
    if not crews_dir.exists():
        return flows

    for entry in crews_dir.iterdir():
        if entry.is_dir() and (entry / "__init__.py").exists() and (entry / "main.py").exists():
            module_name = f"app.crews.{entry.name}.main"
            try:
                module = importlib.import_module(module_name)
            except Exception:
                continue
            kickoff = getattr(module, "kickoff", None)
            if kickoff is not None and callable(kickoff):
                flows[entry.name] = kickoff

    return flows


_FLOWS = _discover_flows()


def _serialize_crew_result(result: object) -> str:
    """Return a JSON-friendly string from a CrewAI flow/crew result."""
    if result is None:
        return ""
    if hasattr(result, "raw"):
        return str(result.raw)
    return str(result)


@router.post("/{flow_name}/kickoff")
def flow_kickoff(flow_name: str, request: FlowKickoffRequest) -> dict:
    """Run a discovered CrewAI flow by name."""
    if flow_name not in _FLOWS:
        raise HTTPException(
            status_code=404,
            detail=f"Flow '{flow_name}' not found. Available flows: {', '.join(sorted(_FLOWS))}",
        )

    if not settings.OPENAI_API_KEY and not settings.ANTHROPIC_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="No LLM API key configured. Set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env.local.",
        )

    kickoff = _FLOWS[flow_name]

    try:
        result = kickoff(request.inputs)
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Crew execution failed: {exc}"
        ) from exc

    return {"flow": flow_name, "inputs": request.inputs, "result": _serialize_crew_result(result)}
