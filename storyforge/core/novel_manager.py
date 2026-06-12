"""
storyforge.core.novel_manager
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Novel registry — JSON metadata + flat-file chapter storage.
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path

NOVELS_DIR = Path("novels")
NOVELS_DIR.mkdir(exist_ok=True)


class NovelManager:
    """Manages all novel metadata and on-disk chapter/summary files."""

    def __init__(self) -> None:
        self.current_novel: str | None = None
        self.metadata: dict = {}

    # ── Create / Load / Save ──────────────────────────────────────────────────

    def create_novel(self, title: str, genre: str, premise: str) -> str:
        novel_id = str(uuid.uuid4())
        metadata = {
            "novel_id":       novel_id,
            "title":          title,
            "genre":          genre,
            "premise":        premise,
            "current_chapter": 1,
            "characters":     [],
            "locations":      [],
            "factions":       [],
            "lore_topics":    [],
            "created":        True,
        }
        self._novel_dir(novel_id).mkdir(parents=True, exist_ok=True)
        self.save_metadata(novel_id, metadata)
        self.current_novel = novel_id
        self.metadata = metadata
        return novel_id

    def load_novel(self, novel_id: str) -> dict:
        path = NOVELS_DIR / f"{novel_id}.json"
        if not path.exists():
            raise FileNotFoundError(f"Novel not found: {novel_id}")
        with open(path, encoding="utf-8") as f:
            metadata = json.load(f)
        self.current_novel = novel_id
        self.metadata = metadata
        return metadata

    def save_metadata(self, novel_id: str, metadata: dict) -> None:
        path = NOVELS_DIR / f"{novel_id}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4, ensure_ascii=False)

    # ── Disk chapter storage ──────────────────────────────────────────────────

    def _novel_dir(self, novel_id: str | None = None) -> Path:
        return NOVELS_DIR / (novel_id or self.current_novel)  # type: ignore[operator]

    def save_chapter_to_disk(
        self, chapter_number: int, chapter_text: str, summary_text: str
    ) -> None:
        d = self._novel_dir()
        d.mkdir(parents=True, exist_ok=True)
        (d / f"chapter_{chapter_number:03d}.txt").write_text(chapter_text, "utf-8")
        (d / f"summary_{chapter_number:03d}.txt").write_text(summary_text, "utf-8")

    def read_chapter_from_disk(self, chapter_number: int) -> str | None:
        path = self._novel_dir() / f"chapter_{chapter_number:03d}.txt"
        return path.read_text("utf-8") if path.exists() else None

    def read_summary_from_disk(self, chapter_number: int) -> str | None:
        path = self._novel_dir() / f"summary_{chapter_number:03d}.txt"
        return path.read_text("utf-8") if path.exists() else None

    def chapter_files(self, novel_id: str | None = None) -> list[Path]:
        d = self._novel_dir(novel_id or self.current_novel)
        return sorted(d.glob("chapter_*.txt")) if d.exists() else []

    # ── Chapter counter ───────────────────────────────────────────────────────

    def update_chapter(self) -> int:
        self.metadata["current_chapter"] += 1
        self.save_metadata(self.current_novel, self.metadata)  # type: ignore[arg-type]
        return self.metadata["current_chapter"]

    def get_current_chapter(self) -> int:
        return self.metadata.get("current_chapter", 1)

    # ── Metadata population ───────────────────────────────────────────────────

    def add_character(self, name: str) -> None:
        if name and name not in self.metadata["characters"]:
            self.metadata["characters"].append(name)
            self.save_metadata(self.current_novel, self.metadata)  # type: ignore[arg-type]

    def add_location(self, location: str) -> None:
        if location and location not in self.metadata["locations"]:
            self.metadata["locations"].append(location)
            self.save_metadata(self.current_novel, self.metadata)  # type: ignore[arg-type]

    def add_faction(self, faction: str) -> None:
        if faction and faction not in self.metadata["factions"]:
            self.metadata["factions"].append(faction)
            self.save_metadata(self.current_novel, self.metadata)  # type: ignore[arg-type]

    def add_lore_topic(self, topic: str) -> None:
        if topic and topic not in self.metadata["lore_topics"]:
            self.metadata["lore_topics"].append(topic)
            self.save_metadata(self.current_novel, self.metadata)  # type: ignore[arg-type]

    def apply_lore_extraction(self, lore_text: str) -> None:
        """Parse structured markdown from extract_lore() into metadata fields."""
        if not lore_text:
            return

        section = None
        location_headers = {"locations", "location"}
        faction_headers  = {"factions", "faction", "political systems", "political system"}
        lore_headers     = {
            "magic systems", "magic system", "technology", "history",
            "world rules", "lore", "other",
        }

        for line in lore_text.splitlines():
            stripped = line.strip()
            if not stripped:
                continue

            # Section header: lines starting with #
            if stripped.startswith("#"):
                header_text = stripped.lstrip("# ").rstrip(":").lower()
                if header_text in location_headers:
                    section = "location"
                elif header_text in faction_headers:
                    section = "faction"
                elif header_text in lore_headers:
                    section = "lore"
                else:
                    section = None
                continue

            # Bullet item under active section
            if stripped.startswith(("-", "*")):
                item = stripped.lstrip("-* ").split(":")[0].strip()
                if not item:
                    continue
                if section == "location":
                    self.add_location(item)
                elif section == "faction":
                    self.add_faction(item)
                elif section == "lore":
                    self.add_lore_topic(item)

    # ── Listing ───────────────────────────────────────────────────────────────

    def list_novels(self) -> list[dict]:
        out = []
        for f in NOVELS_DIR.glob("*.json"):
            try:
                data = json.loads(f.read_text("utf-8"))
                out.append(
                    {
                        "novel_id": data.get("novel_id"),
                        "title":    data.get("title"),
                        "genre":    data.get("genre"),
                        "chapter":  data.get("current_chapter", 1),
                    }
                )
            except Exception:
                pass
        return out

    def delete_novel(self, novel_id: str) -> None:
        path = NOVELS_DIR / f"{novel_id}.json"
        if path.exists():
            path.unlink()

    # ── Accessors ─────────────────────────────────────────────────────────────

    def get_metadata(self) -> dict:
        return self.metadata

    def get_novel_id(self) -> str | None:
        return self.current_novel

    def get_story_bible(self) -> str:
        m = self.metadata
        return (
            f"Title:\n{m.get('title', '')}\n\n"
            f"Genre:\n{m.get('genre', '')}\n\n"
            f"Premise:\n{m.get('premise', '')}\n\n"
            f"Characters:\n{', '.join(m.get('characters', []))}\n\n"
            f"Locations:\n{', '.join(m.get('locations', []))}\n\n"
            f"Factions:\n{', '.join(m.get('factions', []))}\n\n"
            f"Lore:\n{', '.join(m.get('lore_topics', []))}\n\n"
            f"Current Chapter:\n{m.get('current_chapter', 1)}"
        )
