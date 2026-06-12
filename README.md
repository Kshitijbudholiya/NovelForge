# StoryForge AI

**AI-powered novel writer** with vector memory, retrieval-augmented generation, and a
dark literary desktop UI built with DearPyGui.

---

## Features

- **Create novels** – give a title, genre, and premise; Chapter 1 is generated automatically
- **Continue stories** – type an instruction to generate the next chapter with full continuity
- **Ask questions** – query any detail about your story; the RAG layer searches all past chapters
- **Interactive / Read-only toggle** – switch between writing mode and browsing saved chapters
- **Sidebar** – collapsible novel tree with per-chapter navigation
- **Chat history** – separate conversation per novel and per chapter, persisted across sessions
- **Story Bible** – auto-populated characters, locations, factions, and lore extracted from each chapter
- **Vector memory** – multi-index Endee DB (story, character, lore, summary) for semantic recall

## Requirements

| Dependency | Purpose |
|---|---|
| [DearPyGui](https://github.com/hoffstadt/DearPyGui) ≥ 2.0 | Desktop GUI |
| [Ollama](https://ollama.ai) | Local LLM inference |
| [Endee](https://github.com/endee-io/endee) | Vector database |

Ollama must be running locally with the **qwen3:8b** and **nomic-embed-text** models pulled:

```bash
ollama pull qwen3:8b
ollama pull nomic-embed-text
```

## Installation

```bash
pip install storyforge
```

## Launch

```bash
storyforge
```

Or from Python:

```python
from storyforge import launch
launch()
```

## Project Layout

```
StoryForge/
├── storyforge/
│   ├── __init__.py          # public API + launch()
│   ├── __main__.py          # python -m storyforge
│   ├── core/
│   │   ├── __init__.py
│   │   ├── prompts.py       # all LLM prompt templates
│   │   ├── generators.py    # LLM calls (create, continue, compress, extract)
│   │   ├── memory.py        # Endee vector DB layer
│   │   ├── novel_manager.py # disk persistence + metadata
│   │   └── rag.py           # RAG orchestration
│   └── ui/
│       ├── __init__.py
│       ├── app.py           # DearPyGui window + main loop
│       ├── theme.py         # colour palette + theme builders
│       ├── sidebar.py       # novel/chapter tree
│       ├── chat.py          # message rendering + input
│       └── modals.py        # New Novel modal
├── tests/
│   ├── __init__.py
│   ├── test_generators.py
│   └── test_novel_manager.py
├── pyproject.toml
├── README.md
└── LICENSE
```

## License

MIT Licence.

Check out LICENCE page to learn more.