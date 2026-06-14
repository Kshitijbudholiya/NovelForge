"""
novelforge.ui.workers
~~~~~~~~~~~~~~~~~~~~~
QThread worker classes for all blocking AI operations.
Each emits typed signals so the UI can react without polling.
"""

from __future__ import annotations

from PyQt6.QtCore import QThread, pyqtSignal


class CreateNovelWorker(QThread):
    """Generate the first chapter of a brand-new novel."""

    progress = pyqtSignal(str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, manager, title: str, genre: str, premise: str) -> None:
        super().__init__()
        self.manager = manager
        self.title = title
        self.genre = genre
        self.premise = premise

    def run(self) -> None:
        try:
            from novelforge.core.generators import (
                create_first_chapter,
                compress_memory,
                extract_characters,
                extract_lore,
            )
            from novelforge.core.rag import save_first_chapter

            self.progress.emit("Creating novel record…")
            nid = self.manager.create_novel(self.title, self.genre, self.premise)

            self.progress.emit("Generating Chapter 1 — this may take a minute…")
            chapter = create_first_chapter(self.premise)

            self.progress.emit("Compressing memory…")
            summary = compress_memory(chapter)

            self.progress.emit("Extracting characters…")
            chars = extract_characters(chapter)

            self.progress.emit("Extracting lore…")
            lore = extract_lore(chapter)

            self.progress.emit("Saving to disk…")
            save_first_chapter(nid, chapter, summary, chars, lore)
            self.manager.save_chapter_to_disk(1, chapter, summary)

            for c in chars:
                if isinstance(c, dict) and c.get("name"):
                    self.manager.add_character(c["name"])
            if lore:
                self.manager.apply_lore_extraction(lore)

            self.finished.emit(
                {
                    "novel_id": nid,
                    "chapter": chapter,
                    "summary": summary,
                    "chars": chars,
                    "lore": lore,
                }
            )

        except Exception as exc:
            self.error.emit(str(exc))


class SendMessageWorker(QThread):
    """Handle a chat message — either Q&A or chapter generation."""

    progress = pyqtSignal(str)
    answer = pyqtSignal(str)
    chapter = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(
        self,
        manager,
        novel_id: str,
        text: str,
        scope: str,
        chapter_number: int | None,
    ) -> None:
        super().__init__()
        self.manager = manager
        self.novel_id = novel_id
        self.text = text
        self.scope = scope
        self.chapter_number = chapter_number

    def run(self) -> None:
        try:
            from novelforge.core.generators import classify_intent
            from novelforge.core.rag import (
                generate_next_chapter,
                ask_story_question,
            )

            bible = self.manager.get_story_bible()
            intent = classify_intent(self.text)

            if intent == "QUESTION" or self.scope == "novel":
                self.progress.emit("Searching story memory…")
                ans = ask_story_question(self.novel_id, self.text, bible)
                self.answer.emit(ans)

            else:
                self.progress.emit("Planning chapter…")
                ch_num = self.manager.update_chapter()

                self.progress.emit(f"Writing Chapter {ch_num}…")
                pkg = generate_next_chapter(self.novel_id, self.text, ch_num, bible)

                self.progress.emit("Saving chapter to disk…")
                self.manager.save_chapter_to_disk(
                    ch_num, pkg["chapter"], pkg["summary"]
                )
                for c in pkg.get("characters", []):
                    if isinstance(c, dict) and c.get("name"):
                        self.manager.add_character(c["name"])
                if pkg.get("lore"):
                    self.manager.apply_lore_extraction(pkg["lore"])

                pkg["chapter_number"] = ch_num
                self.chapter.emit(pkg)

        except Exception as exc:
            self.error.emit(str(exc))
