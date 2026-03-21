from rich.console import Console
from rich.tree import Tree
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint
from rich.text import Text

from agent.graph import KnowledgeGraph

console = Console()

def print_header(topic: str):
    """Print the Paradosis header."""
    console.print(Panel.fit(
        f"[bold white]PARADOSIS[/bold white]  •  [bold yellow]{topic}[/bold yellow]\n"
        f"[dim]παράδοσις — Knowledge, traced to its origin[/dim]",
        border_style="yellow"
    ))

def print_graph(graph: KnowledgeGraph):
    """Print the knowledge graph as a rich tree."""
    
    # Build the tree from root
    root_node = graph.nodes.get(graph.root_topic)
    if not root_node:
        console.print("[red]No root node found[/red]")
        return
    
    # Source color mapping
    source_colors = {
        "Wikipedia": "cyan",
        "Web": "green",
        "Guardian": "magenta"
    }
    
    def source_badge(source: str) -> str:
        color = source_colors.get(source, "white")
        return f"[{color}][{source[:4]}][/{color}]"
    
    def confidence_bar(confidence: float) -> str:
        if confidence >= 0.8:
            return "[green]●[/green]"
        elif confidence >= 0.5:
            return "[yellow]●[/yellow]"
        else:
            return "[red]●[/red]"
    
    # Root
    root_label = (
        f"{confidence_bar(root_node.confidence)} "
        f"[bold white]{root_node.concept}[/bold white] "
        f"{source_badge(root_node.source)}"
    )
    tree = Tree(root_label)
    
    # Children
    children = graph.get_children(graph.root_topic)
    for child_name in children:
        child_node = graph.nodes.get(child_name)
        if not child_node:
            continue
        
        edge_data = graph.graph.edges.get(
            (graph.root_topic, child_name), {}
        )
        relationship = edge_data.get("relationship", "related_to")
        
        child_label = (
            f"{confidence_bar(child_node.confidence)} "
            f"[bold]{child_node.concept}[/bold] "
            f"{source_badge(child_node.source)} "
            f"[dim]{relationship}[/dim]"
        )
        branch = tree.add(child_label)
        
        # Grandchildren
        grandchildren = graph.get_children(child_name)
        for gc_name in grandchildren:
            gc_node = graph.nodes.get(gc_name)
            if not gc_node:
                continue
            gc_label = (
                f"{confidence_bar(gc_node.confidence)} "
                f"{gc_node.concept} "
                f"{source_badge(gc_node.source)}"
            )
            branch.add(gc_label)
    
    console.print(tree)

def print_isnad(graph: KnowledgeGraph, concept: str):
    """Print the full provenance chain for a concept."""
    isnad = graph.get_isnad(concept)
    if not isnad:
        console.print(f"[red]Concept '{concept}' not found in graph[/red]")
        return
    
    table = Table(title=f"Isnad Chain — {concept}", border_style="yellow")
    table.add_column("Field", style="dim", width=15)
    table.add_column("Value", style="white")
    
    table.add_row("Concept", isnad["concept"])
    table.add_row("Source", isnad["source"])
    table.add_row("URL", isnad["url"])
    table.add_row("Fetched At", isnad["fetched_at"])
    table.add_row("Confidence", f"{isnad['confidence']:.0%}")
    table.add_row("Depth", str(isnad["depth"]))
    table.add_row("Summary", isnad["summary"][:200] + "...")
    
    console.print(table)

def print_stats(graph: KnowledgeGraph, elapsed: float):
    """Print final graph statistics."""
    console.print(
        f"\n[dim]─────────────────────────────────────────[/dim]\n"
        f" [bold]{graph.total_nodes()}[/bold] nodes  •  "
        f"[bold]{graph.total_edges()}[/bold] edges  •  "
        f"[bold]1[/bold] source  •  "
        f"[bold]{elapsed:.1f}s[/bold]\n"
        f"[dim]─────────────────────────────────────────[/dim]"
    )