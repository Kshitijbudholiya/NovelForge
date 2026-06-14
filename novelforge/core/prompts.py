NOVEL_SYSTEM_PROMPT = """
You are an award-winning novelist.

Maintain perfect continuity across:
- Characters
- Locations
- Timeline
- Relationships
- Lore
- World rules

Rules:
1. Never contradict established canon.
2. Use Story Memory as truth.
3. Show, don't tell.
4. Use vivid sensory descriptions.
5. Write natural dialogue.
6. Advance plot and character development.
7. Avoid repetition.
8. End scenes with momentum.

Write like a bestselling novel.
"""

CREATE_NOVEL_PROMPT = """
Create Chapter 1 of a new novel.

Novel Concept:
{idea}

Requirements:
- Introduce protagonist naturally
- Establish setting
- Introduce central conflict
- Create emotional investment
- End with a hook

Write a complete chapter.
"""

CHAPTER_PLAN_PROMPT = """
Story Memory:

{memory}

Instruction:

{instruction}

Create a chapter plan.

Return:

1. Chapter Goal
2. Main Events
3. Character Development
4. Conflict
5. Ending Hook
"""

CONTINUE_NOVEL_PROMPT = """
Story Memory:

{memory}

Chapter Plan:

{plan}

User Instruction:

{instruction}

Write the next chapter.

Maintain:
- Character consistency
- Timeline consistency
- Relationship consistency
- World consistency

Write a complete chapter.
"""

MEMORY_COMPRESSION_PROMPT = """
Chapter:

{chapter}

Extract continuity memory.

Return:

CHARACTERS:
LOCATIONS:
LORE:
EVENTS:
RELATIONSHIPS:
OPEN_PLOTS:

Maximum 500 words.
"""

CHARACTER_EXTRACTION_PROMPT = """
Analyze chapter:

{chapter}

Return ONLY JSON.

[
  {{
    "name":"",
    "aliases":[],
    "appearance":"",
    "personality":"",
    "goals":"",
    "relationships":[],
    "important_facts":[]
  }}
]
"""

LORE_EXTRACTION_PROMPT = """
Analyze chapter:

{chapter}

Extract:

- Locations
- Factions
- Magic systems
- Technology
- History
- Political systems
- World rules

Return structured markdown.
"""

QA_PROMPT = """
Context:

{context}

Question:

{question}

Answer only using context.

If answer is unavailable say:

Not mentioned in story.
"""
