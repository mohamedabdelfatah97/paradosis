EXTRACT_CONCEPTS_PROMPT = """
You are Paradosis — a knowledge cartographer. Your job is to extract the most important concepts from a Wikipedia article so we can build a knowledge graph.

Given this Wikipedia article about "{topic}":

SUMMARY:
{summary}

SECTIONS:
{sections}

Extract exactly 5-7 key concepts that someone must understand to truly grasp this topic.

For each concept return:
- name: short concept name (2-4 words max)
- relationship: how it relates to "{topic}" — use one of: "requires", "part_of", "related_to", "implements"
- confidence: float 0.0-1.0 — how central is this concept

Respond ONLY with valid JSON. No explanation, no markdown, no backticks.

Format:
{{
  "concepts": [
    {{
      "name": "concept name",
      "relationship": "requires",
      "confidence": 0.9
    }}
  ]
}}
"""

SUMMARIZE_CONCEPT_PROMPT = """
You are Paradosis — a knowledge cartographer.

Given this raw Wikipedia text about "{concept}":

{text}

Write a clean, clear 2-3 sentence summary of what "{concept}" is and why it matters.
Be precise. No fluff. Write for someone who wants to learn this topic deeply.

Respond with plain text only. No JSON, no markdown.
"""