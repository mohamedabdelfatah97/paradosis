import asyncio
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("wikipedia")

@mcp.tool()
async def fetch_article(topic: str) -> dict:
    """Fetch a Wikipedia article summary and key sections for a given topic."""
    
    async with httpx.AsyncClient(
        headers={
            "User-Agent": "Paradosis/1.0 (educational knowledge tool; https://github.com)",
            "Accept": "application/json"
        },
        follow_redirects=True,
        timeout=30.0
    ) as client:
        try:
            # Step 1 — search for the best matching article
            search_url = "https://en.wikipedia.org/w/api.php"
            search_params = {
                "action": "query",
                "list": "search",
                "srsearch": topic,
                "format": "json",
                "srlimit": 3,
                "srinfo": "totalhits",
                "srprop": "snippet|titlesnippet"
            }
            search_resp = await client.get(search_url, params=search_params)
            
            if search_resp.status_code == 403:
                return {"error": f"Wikipedia rate limit hit (403). Try again in a few minutes."}
            
            if search_resp.status_code != 200:
                return {"error": f"Wikipedia search failed with status {search_resp.status_code}"}
            
            await asyncio.sleep(1)
            search_data = search_resp.json()
            
            if not search_data.get("query", {}).get("search"):
                return {"error": f"No Wikipedia article found for '{topic}'"}
            
            results = search_data["query"]["search"]
            topic_lower = topic.lower().replace("-", " ").replace("_", " ")
            page_title = None
            for result in results:
                title_lower = result["title"].lower()
                if any(word in title_lower for word in topic_lower.split() if len(word) > 3):
                    page_title = result["title"]
                    break

            if not page_title:
                return {"error": f"No relevant Wikipedia article found for '{topic}'. Wikipedia may not have this topic."}
                        
            # Step 2 — fetch the actual article summary
            summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{page_title}"
            summary_resp = await client.get(summary_url)
            
            if summary_resp.status_code != 200:
                return {"error": f"Wikipedia summary fetch failed for '{page_title}'"}
            
            await asyncio.sleep(1)
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
            await asyncio.sleep(1)
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
        
        except Exception as e:
            return {"error": str(e)}

if __name__ == "__main__":
    mcp.run()