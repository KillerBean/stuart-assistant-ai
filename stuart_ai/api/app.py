from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from stuart_ai.core.state import AssistantContext

try:
    from fastapi import FastAPI
except ImportError as exc:
    raise ImportError("fastapi not installed. Run: uv add fastapi uvicorn") from exc

app = FastAPI(title="Stuart AI Management API", version="0.1.0")

_context: AssistantContext | None = None
_available_agents: list[dict] = [
    {"name": "web_search", "description": "Busca na web via DuckDuckGo com síntese por LLM"},
    {"name": "rag", "description": "Recuperação de documentos locais (RAG + ChromaDB)"},
    {"name": "calendar", "description": "Gerenciamento de agenda (.ics)"},
    {"name": "content", "description": "Resumo de artigos web e vídeos do YouTube"},
    {"name": "coding", "description": "Análise de erros, geração de scripts e revisão de código"},
]


def set_context(context: AssistantContext):
    global _context  # pylint: disable=global-statement
    _context = context


@app.get("/status")
def get_status():
    if _context is None:
        return {"status": "not_initialized"}
    return {
        "status": _context.status.value,
        "last_command": _context.last_command,
        "last_response": _context.last_response,
        "command_count": _context.command_count,
        "uptime_seconds": _context.uptime_seconds(),
    }


@app.get("/agents/list")
def list_agents():
    return {"agents": _available_agents}


@app.get("/logs")
def get_logs():
    """Returns the last lines from the log file if available."""
    import os  # pylint: disable=import-outside-toplevel
    log_path = "stuart.log"
    if not os.path.exists(log_path):
        return {"logs": [], "message": "Log file not found"}
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return {"logs": lines[-100:]}
    except OSError:
        return {"logs": [], "message": "Could not read log file"}
