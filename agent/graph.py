from dataclasses import dataclass, field
from datetime import datetime
import networkx as nx

@dataclass
class Node:
    """A single concept in the knowledge graph."""
    concept: str
    summary: str
    source: str          # "Wikipedia", "Web", "Guardian"
    url: str             # exact source URL
    fetched_at: str      # timestamp
    confidence: float    # 0.0 - 1.0
    depth: int           # how deep in the graph

@dataclass 
class Edge:
    """A relationship between two concepts."""
    from_concept: str
    to_concept: str
    relationship: str    # "requires", "part_of", "related_to", "implements"

class KnowledgeGraph:
    """The full Paradosis knowledge graph for a topic."""
    
    def __init__(self, root_topic: str):
        self.root_topic = root_topic
        self.graph = nx.DiGraph()
        self.nodes: dict[str, Node] = {}
        self.created_at = datetime.now().isoformat()
    
    def add_node(self, node: Node):
        """Add a concept node to the graph."""
        self.nodes[node.concept] = node
        self.graph.add_node(
            node.concept,
            summary=node.summary,
            source=node.source,
            url=node.url,
            fetched_at=node.fetched_at,
            confidence=node.confidence,
            depth=node.depth
        )
    
    def add_edge(self, edge: Edge):
        """Add a relationship between two concepts."""
        self.graph.add_edge(
            edge.from_concept,
            edge.to_concept,
            relationship=edge.relationship
        )
    
    def get_isnad(self, concept: str) -> dict:
        """Get the full provenance chain for a concept — its isnad."""
        if concept not in self.nodes:
            return {}
        node = self.nodes[concept]
        return {
            "concept": node.concept,
            "source": node.source,
            "url": node.url,
            "fetched_at": node.fetched_at,
            "confidence": node.confidence,
            "depth": node.depth,
            "summary": node.summary
        }
    
    def get_children(self, concept: str) -> list[str]:
        """Get all concepts that stem from this concept."""
        return list(self.graph.successors(concept))
    
    def total_nodes(self) -> int:
        return len(self.nodes)
    
    def total_edges(self) -> int:
        return self.graph.number_of_edges()