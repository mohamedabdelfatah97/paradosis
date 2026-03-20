import asyncio
import json
import os
from datetime import datetime

import google.generativeai as genai
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv

from agent.graph import KnowledgeGraph, Node, Edge
from agent.prompts import EXTRACT_CONCEPTS_PROMPT, SUMMARIZE_CONCEPT_PROMPT

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

async def fetch_from_wikipedia(topic: str) -> dict:
    """Call the Wikipedia MCP server and get article data."""
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_servers/wikipedia_server.py"]
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(
                "fetch_article",
                arguments={"topic": topic}
            )
            return json.loads(result.content[0].text)

def extract_concepts_with_gemini(topic: str, wiki_data: dict) -> list[dict]:
    """Ask Gemini to extract key concepts from the Wikipedia data."""
    prompt = EXTRACT_CONCEPTS_PROMPT.format(
        topic=topic,
        summary=wiki_data.get("summary", "")[:2000],
        sections=", ".join(wiki_data.get("sections", []))
    )
    response = model.generate_content(prompt)
    text = response.text.strip()
    
    # Clean any accidental markdown
    text = text.replace("```json", "").replace("```", "").strip()
    
    parsed = json.loads(text)
    return parsed.get("concepts", [])

def summarize_concept_with_gemini(concept: str, raw_text: str) -> str:
    """Ask Gemini to write a clean summary of a concept."""
    prompt = SUMMARIZE_CONCEPT_PROMPT.format(
        concept=concept,
        text=raw_text[:1500]
    )
    response = model.generate_content(prompt)
    return response.text.strip()

async def build_graph(topic: str, depth: int = 2) -> KnowledgeGraph:
    """
    Core Paradosis agent loop.
    Fetches Wikipedia data, extracts concepts, builds knowledge graph.
    """
    graph = KnowledgeGraph(root_topic=topic)
    
    print(f"\n🔍 Fetching Wikipedia data for '{topic}'...")
    wiki_data = await fetch_from_wikipedia(topic)
    
    if "error" in wiki_data:
        print(f"❌ {wiki_data['error']}")
        return graph
    
    # Add root node
    root_node = Node(
        concept=topic,
        summary=wiki_data["summary"][:300],
        source="Wikipedia",
        url=wiki_data["url"],
        fetched_at=datetime.now().isoformat(),
        confidence=1.0,
        depth=0
    )
    graph.add_node(root_node)
    print(f"✓ Root node added: {topic}")
    
    # Extract concepts with Gemini
    print(f"🧠 Extracting key concepts with Gemini...")
    concepts = extract_concepts_with_gemini(topic, wiki_data)
    print(f"✓ Found {len(concepts)} concepts")
    
    # For each concept — fetch Wikipedia + add to graph
    for concept_data in concepts:
        concept_name = concept_data["name"]
        print(f"  → Fetching '{concept_name}'...")
        
        try:
            concept_wiki = await fetch_from_wikipedia(concept_name)
            
            if "error" not in concept_wiki:
                summary = summarize_concept_with_gemini(
                    concept_name,
                    concept_wiki["summary"]
                )
                node = Node(
                    concept=concept_name,
                    summary=summary,
                    source="Wikipedia",
                    url=concept_wiki["url"],
                    fetched_at=datetime.now().isoformat(),
                    confidence=concept_data.get("confidence", 0.7),
                    depth=1
                )
                graph.add_node(node)
                graph.add_edge(Edge(
                    from_concept=topic,
                    to_concept=concept_name,
                    relationship=concept_data.get("relationship", "related_to")
                ))
        except Exception as e:
            print(f"  ⚠ Skipping '{concept_name}': {e}")
            continue
    
    return graph