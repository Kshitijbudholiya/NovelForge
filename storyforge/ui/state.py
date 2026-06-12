"""
storyforge.ui.state
~~~~~~~~~~~~~~~~~~~
Shared mutable application state — single module imported by all UI layers.
Avoids circular imports by keeping state separate from logic.
"""

from __future__ import annotations

from pathlib import Path
import json

# ── runtime flags ─────────────────────────────────────────────────────────────

interactive: bool = True    # toggle: write mode vs read-only
busy: bool = False          # True while a generation thread is running

# ── active selection ──────────────────────────────────────────────────────────

active_novel: str | None = None   # novel_id of the currently viewed novel
active_scope: str = "novel"       # "novel" | "chapter"
active_chap: int | None = None    # chapter number when scope == "chapter"

# ── chat history ──────────────────────────────────────────────────────────────
# key: novel_id (novel-level chat)  OR  "{novel_id}_ch{n}" (chapter chat)
# value: list of {"role": str, "text": str, "time": str}

chat_history: dict[str, list[dict]] = {}

# ── sidebar node registry ─────────────────────────────────────────────────────
# novel_id -> {"tree_node": dpg_tag, "chapters": {chapter_num: dpg_tag}}

sidebar_nodes: dict[str, dict] = {}

# ── manager reference (set by app.py after import) ───────────────────────────

manager = None   # storyforge.core.novel_manager.NovelManager | None

# ── helpers ───────────────────────────────────────────────────────────────────

NOVELS_DIR = Path("novels")


def chat_key() -> str:
    if active_scope == "chapter" and active_chap is not None:
        return f"{active_novel}_ch{active_chap}"
    return active_novel or "__home__"


def get_chat() -> list[dict]:
    return chat_history.setdefault(chat_key(), [])


def novels_on_disk() -> list[dict]:
    out = []
    for f in NOVELS_DIR.glob("*.json"):
        try:
            out.append(json.loads(f.read_text("utf-8")))
        except Exception:
            pass
    return out


def chapter_files(novel_id: str) -> list[Path]:
    d = NOVELS_DIR / novel_id
    return sorted(d.glob("chapter_*.txt")) if d.exists() else []
