import httpx
from mcp.server.fastmcp import FastMCP
import asyncio
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("wikipedia")

@mcp.tool()
async def fetch_article(topic: str) -> dict:
    """Fetch a Wikipedia article summary and key sections for a given topic."""
    
    async with httpx.AsyncClient(
    headers={
        "User-Agent": "Paradosis/1.0 (knowledge cartography; contact: educational-tool)",
        "Accept": "application/json"
    },
    follow_redirects=True,
    timeout=30.0
) as client:
        # Step 1 — search for the best matching article
        search_url = "https://en.wikipedia.org/w/api.php"
        search_params = {
            "action": "query",
            "list": "search",
            "srsearch": topic,
            "format": "json",
            "srlimit": 1
        }
        search_resp = await client.get(search_url, params=search_params)
        search_data = search_resp.json()
        await asyncio.sleep(1)
        
        if not search_data["query"]["search"]:
            return {"error": f"No Wikipedia article found for '{topic}'"}
        
        page_title = search_data["query"]["search"][0]["title"]
        
        # Step 2 — fetch the actual article summary
        summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{page_title}"
        summary_resp = await client.get(summary_url)
        summary_data = summary_resp.json()
        
        # Step 3 — fetch sections
        sections_url = "https://en.wikipedia.org/w/api.php"
        sections_params = {
            "action": "parse",
            "page": page_title,
            "prop": "sections",
            "format": "json"
        }
        sections_resp = await client.get(sections_url, params=sections_params)
        sections_data = sections_resp.json()
        
        sections = []
        if "parse" in sections_data:
            sections = [
                s["line"] for s in sections_data["parse"]["sections"]
                if s["toclevel"] == 1
            ]
        
        return {
            "title": page_title,
            "summary": summary_data.get("extract", ""),
            "sections": sections,
            "url": summary_data.get("content_urls", {}).get("desktop", {}).get("page", ""),
            "source": "Wikipedia"
        }

if __name__ == "__main__":
    mcp.run()