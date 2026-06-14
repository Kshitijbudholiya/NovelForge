from __future__ import annotations

from functools import lru_cache

from endee import Endee, Precision
import ollama

STORY_INDEX = "story_memory"
CHARACTER_INDEX = "character_memory"
LORE_INDEX = "lore_memory"
SUMMARY_INDEX = "summary_memory"

EMBED_MODEL = "nomic-embed-text"

EMBED_GPU_OPTIONS = {
    "num_gpu": -1,
    "main_gpu": 0,
    "num_batch": 512,
    "f16_kv": True,
    "use_mmap": True,
    "num_thread": 0,
}


@lru_cache(maxsize=None)
def _client() -> Endee:
    return Endee()


def _ensure_index(name: str):
    client = _client()
    try:
        return client.get_index(name)
    except Exception:
        client.create_index(
            name=name,
            dimension=768,
            space_type="cosine",
            precision=Precision.INT8,
        )
        return client.get_index(name)


@lru_cache(maxsize=None)
def _story_index():
    return _ensure_index(STORY_INDEX)


@lru_cache(maxsize=None)
def _character_index():
    return _ensure_index(CHARACTER_INDEX)


@lru_cache(maxsize=None)
def _lore_index():
    return _ensure_index(LORE_INDEX)


@lru_cache(maxsize=None)
def _summary_index():
    return _ensure_index(SUMMARY_INDEX)


def get_embedding(text: str) -> list[float]:
    response = ollama.embeddings(
        model=EMBED_MODEL,
        prompt=text,
        options=EMBED_GPU_OPTIONS,
    )
    return response["embedding"]


def chunk_text(text: str, chunk_size: int = 400) -> list[str]:
    words = text.split()
    return [
        " ".join(words[i : i + chunk_size]) for i in range(0, len(words), chunk_size)
    ]


def _upsert(
    index, novel_id: str, doc_type: str, chapter_number: int, text: str
) -> None:
    vectors = []
    for i, chunk in enumerate(chunk_text(text)):
        vectors.append(
            {
                "id": f"{novel_id}_{doc_type}_{chapter_number}_{i}",
                "vector": get_embedding(chunk),
                "meta": {
                    "novel_id": novel_id,
                    "doc_type": doc_type,
                    "chapter": chapter_number,
                    "text": chunk,
                },
                "filter": {
                    "novel_id": novel_id,
                    "chapter": str(chapter_number),
                },
            }
        )
    if vectors:
        index.upsert(vectors)


def save_story(novel_id: str, chapter_number: int, text: str) -> None:
    _upsert(_story_index(), novel_id, "story", chapter_number, text)


def save_summary(novel_id: str, chapter_number: int, text: str) -> None:
    _upsert(_summary_index(), novel_id, "summary", chapter_number, text)


def save_characters(novel_id: str, chapter_number: int, text: str) -> None:
    _upsert(_character_index(), novel_id, "characters", chapter_number, text)


def save_lore(novel_id: str, chapter_number: int, text: str) -> None:
    _upsert(_lore_index(), novel_id, "lore", chapter_number, text)


def search_index(index, novel_id: str, query: str, top_k: int = 5) -> str:
    results = index.query(
        vector=get_embedding(query),
        top_k=top_k,
        filter=[{"novel_id": {"$eq": novel_id}}],
    )
    memories = [
        item["meta"]["text"] for item in results if item.get("meta", {}).get("text")
    ]
    return "\n\n".join(memories)


def retrieve_story_memory(novel_id: str, query: str, top_k: int = 5) -> str:
    return search_index(_story_index(), novel_id, query, top_k)


def retrieve_character_memory(novel_id: str, query: str, top_k: int = 5) -> str:
    return search_index(_character_index(), novel_id, query, top_k)


def retrieve_lore_memory(novel_id: str, query: str, top_k: int = 5) -> str:
    return search_index(_lore_index(), novel_id, query, top_k)


def retrieve_summary_memory(novel_id: str, query: str, top_k: int = 5) -> str:
    return search_index(_summary_index(), novel_id, query, top_k)


def retrieve_all_memory(novel_id: str, query: str) -> str:
    story = retrieve_story_memory(novel_id, query, top_k=8)
    characters = retrieve_character_memory(novel_id, query, top_k=6)
    lore = retrieve_lore_memory(novel_id, query, top_k=6)
    summaries = retrieve_summary_memory(novel_id, query, top_k=8)
    return f"""
=== STORY ===
{story}

=== CHARACTERS ===
{characters}

=== LORE ===
{lore}

=== SUMMARIES ===
{summaries}
"""
