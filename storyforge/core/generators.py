"""
storyforge.core.generators
~~~~~~~~~~~~~~~~~~~~~~~~~~
Core AI generation layer — all Ollama calls live here.
"""

from __future__ import annotations

import json

import ollama

from storyforge.core.prompts import (
    NOVEL_SYSTEM_PROMPT,
    CREATE_NOVEL_PROMPT,
    CHAPTER_PLAN_PROMPT,
    CONTINUE_NOVEL_PROMPT,
    MEMORY_COMPRESSION_PROMPT,
    CHARACTER_EXTRACTION_PROMPT,
    LORE_EXTRACTION_PROMPT,
    QA_PROMPT,
)

STORY_MODEL = "qwen3:8b"


# ── low-level LLM wrapper ─────────────────────────────────────────────────────

def llm(
    prompt: str,
    system: str = NOVEL_SYSTEM_PROMPT,
    temperature: float = 0.8,
) -> str:
    response = ollama.chat(
        model=STORY_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": prompt},
        ],
        options={"temperature": temperature},
    )
    return response["message"]["content"]


# ── intent classification ─────────────────────────────────────────────────────

def classify_intent(user_input: str) -> str:
    """Return 'NEW_NOVEL', 'QUESTION', or 'CONTINUE'."""
    text = user_input.lower().strip()

    new_keywords = [
        "new novel", "new story", "write a novel",
        "create a novel", "start a novel", "novel idea",
    ]
    question_keywords = ["who", "what", "when", "where", "why", "how"]

    if any(k in text for k in new_keywords):
        return "NEW_NOVEL"
    if "?" in text:
        return "QUESTION"
    if any(text.startswith(k) for k in question_keywords):
        return "QUESTION"
    return "CONTINUE"


# ── generation helpers ────────────────────────────────────────────────────────

def create_first_chapter(idea: str) -> str:
    return llm(CREATE_NOVEL_PROMPT.format(idea=idea))


def create_chapter_plan(memory: str, instruction: str) -> str:
    return llm(
        CHAPTER_PLAN_PROMPT.format(memory=memory, instruction=instruction),
        temperature=0.4,
    )


def generate_chapter(memory: str, plan: str, instruction: str) -> str:
    return llm(
        CONTINUE_NOVEL_PROMPT.format(
            memory=memory, plan=plan, instruction=instruction
        )
    )


def compress_memory(chapter: str) -> str:
    return llm(
        MEMORY_COMPRESSION_PROMPT.format(chapter=chapter),
        temperature=0.2,
    )


def extract_characters(chapter: str) -> list[dict]:
    result = llm(
        CHARACTER_EXTRACTION_PROMPT.format(chapter=chapter),
        temperature=0.1,
    )
    try:
        return json.loads(result)
    except Exception:
        return []


def extract_lore(chapter: str) -> str:
    return llm(
        LORE_EXTRACTION_PROMPT.format(chapter=chapter),
        temperature=0.2,
    )


def answer_story_question(context: str, question: str) -> str:
    return llm(
        QA_PROMPT.format(context=context, question=question),
        temperature=0.1,
    )


# ── high-level package ────────────────────────────────────────────────────────

def generate_story_package(memory: str, instruction: str) -> dict:
    """Run the full chapter-generation pipeline and return a results dict."""
    plan      = create_chapter_plan(memory, instruction)
    chapter   = generate_chapter(memory, plan, instruction)
    summary   = compress_memory(chapter)
    characters = extract_characters(chapter)
    lore      = extract_lore(chapter)

    return {
        "plan":       plan,
        "chapter":    chapter,
        "summary":    summary,
        "characters": characters,
        "lore":       lore,
    }
