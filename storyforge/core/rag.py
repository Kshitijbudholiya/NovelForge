"""
storyforge.core.rag
~~~~~~~~~~~~~~~~~~~
RAG orchestration — bridges memory retrieval and generation.
"""

from __future__ import annotations

from storyforge.core.memory import (
    retrieve_all_memory,
    save_story,
    save_summary,
    save_characters,
    save_lore,
)
from storyforge.core.generators import generate_story_package, answer_story_question


# ── context builder ───────────────────────────────────────────────────────────

def build_context(novel_id: str, query: str, story_bible: str = "") -> str:
    memory = retrieve_all_memory(novel_id, query)
    return f"""
=== STORY BIBLE ===

{story_bible}

=== RETRIEVED MEMORY ===

{memory}
"""


# ── chapter generation ────────────────────────────────────────────────────────

def generate_next_chapter(
    novel_id: str,
    instruction: str,
    chapter_number: int,
    story_bible: str = "",
) -> dict:
    context = build_context(novel_id, instruction, story_bible)
    package = generate_story_package(context, instruction)

    save_story(novel_id, chapter_number, package["chapter"])
    save_summary(novel_id, chapter_number, package["summary"])
    save_characters(novel_id, chapter_number, str(package["characters"]))
    save_lore(novel_id, chapter_number, package["lore"])

    return package


# ── question answering ────────────────────────────────────────────────────────

def ask_story_question(
    novel_id: str,
    question: str,
    story_bible: str = "",
) -> str:
    context = build_context(novel_id, question, story_bible)
    return answer_story_question(context, question)


# ── first chapter save ────────────────────────────────────────────────────────

def save_first_chapter(
    novel_id: str,
    chapter_text: str,
    summary: str,
    characters: list,
    lore: str,
) -> None:
    save_story(novel_id, 1, chapter_text)
    save_summary(novel_id, 1, summary)
    save_characters(novel_id, 1, str(characters))
    save_lore(novel_id, 1, lore)


# ── context retrieval (for external use) ─────────────────────────────────────

def retrieve_story_context(
    novel_id: str,
    query: str,
    story_bible: str = "",
) -> str:
    return build_context(novel_id, query, story_bible)
