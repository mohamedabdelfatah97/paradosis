import asyncio
import sys
import time
from dotenv import load_dotenv

from agent.brain import build_graph
from display.terminal import (
    print_header,
    print_graph,
    print_isnad,
    print_stats
)

load_dotenv()

async def main():
    # Get topic from command line
    if len(sys.argv) < 2:
        print("Usage: python main.py \"your topic here\"")
        print("Example: python main.py \"Micro-ROS\"")
        sys.exit(1)
    
    topic = " ".join(sys.argv[1:])
    
    # Print header
    print_header(topic)
    
    # Build the graph
    start = time.time()
    graph = await build_graph(topic, depth=2)
    elapsed = time.time() - start
    
    # Print the knowledge tree
    print_graph(graph)
    
    # Print stats
    print_stats(graph, elapsed)
    
    # Interactive isnad lookup
    if graph.total_nodes() > 0:
        print("\n[Press Enter to inspect a node's isnad chain, or type 'exit' to quit]")
        while True:
            try:
                concept = input("\n→ Enter concept name: ").strip()
                if concept.lower() == "exit" or concept == "":
                    break
                print_isnad(graph, concept)
            except (KeyboardInterrupt, EOFError):
                break
    
    print("\n[dim]παράδοσις[/dim]\n")

if __name__ == "__main__":
    asyncio.run(main())