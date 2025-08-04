"""Graph search models for MOA SDK."""

from typing import Any, Dict, List, Optional

from .base import MOABaseModel

try:
    from pydantic import Field
except ImportError:

    def Field(*args, **kwargs):
        return None


class GraphSearchRequest(MOABaseModel):
    """Request model for graph-based search operations."""

    query: str = Field(..., min_length=1, max_length=1000, description="Search query")
    search_type: str = Field(..., description="Type of graph search")
    max_depth: int = Field(3, ge=1, le=5, description="Maximum search depth")
    max_results: int = Field(20, ge=1, le=100, description="Maximum number of results")
    min_relationship_strength: float = Field(
        0.3, ge=0.0, le=1.0, description="Minimum relationship strength"
    )
    min_concept_relevance: float = Field(
        0.4, ge=0.0, le=1.0, description="Minimum concept relevance"
    )
    include_relationship_types: Optional[List[str]] = Field(
        None, description="Relationship types to include"
    )
    exclude_relationship_types: Optional[List[str]] = Field(
        None, description="Relationship types to exclude"
    )
    weight_by_recency: bool = Field(True, description="Weight results by recency")
    weight_by_access_frequency: bool = Field(
        True, description="Weight results by access frequency"
    )
    boost_direct_connections: float = Field(
        1.5, ge=1.0, le=3.0, description="Boost factor for direct connections"
    )


class GraphNode(MOABaseModel):
    """Graph node model representing a memory in the graph."""

    memory_id: str = Field(..., description="Memory identifier")
    content: str = Field(..., description="Memory content")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Memory metadata"
    )
    tags: List[str] = Field(default_factory=list, description="Memory tags")
    node_type: str = Field("memory", description="Type of graph node")
    centrality_score: Optional[float] = Field(None, description="Node centrality score")
    clustering_coefficient: Optional[float] = Field(
        None, description="Node clustering coefficient"
    )


class GraphRelationship(MOABaseModel):
    """Graph relationship model."""

    source_id: str = Field(..., description="Source memory ID")
    target_id: str = Field(..., description="Target memory ID")
    relationship_type: str = Field(..., description="Type of relationship")
    strength: float = Field(..., ge=0.0, le=1.0, description="Relationship strength")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Relationship metadata"
    )
    created_at: Optional[str] = Field(
        None, description="Relationship creation timestamp"
    )
    confidence: Optional[float] = Field(
        None, description="Relationship confidence score"
    )


class GraphPath(MOABaseModel):
    """Graph path model representing a path between nodes."""

    nodes: List[str] = Field(..., description="List of node IDs in the path")
    relationships: List[GraphRelationship] = Field(
        ..., description="Relationships in the path"
    )
    total_strength: float = Field(..., description="Total path strength")
    path_length: int = Field(..., description="Number of hops in the path")
    path_type: str = Field(..., description="Type of path (shortest, strongest, etc.)")


class GraphSearchResult(MOABaseModel):
    """Individual graph search result."""

    node: GraphNode = Field(..., description="The found graph node")
    score: float = Field(..., description="Relevance score")
    path: Optional[GraphPath] = Field(None, description="Path from query to result")
    related_nodes: List[GraphNode] = Field(
        default_factory=list, description="Related nodes"
    )
    explanation: Optional[str] = Field(None, description="Search result explanation")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional result metadata"
    )


class GraphSearchResponse(MOABaseModel):
    """Response model for graph search operations."""

    results: List[GraphSearchResult] = Field(..., description="Search results")
    total_results: int = Field(..., description="Total number of results")
    search_type: str = Field(..., description="Type of search performed")
    execution_time_ms: int = Field(
        ..., description="Search execution time in milliseconds"
    )
    graph_stats: Dict[str, Any] = Field(..., description="Graph statistics")
    search_config: Dict[str, Any] = Field(..., description="Search configuration used")


class GraphSearchType(MOABaseModel):
    """Available graph search type information."""

    type_name: str = Field(..., description="Search type identifier")
    display_name: str = Field(..., description="Human-readable search type name")
    description: str = Field(..., description="Search type description")
    parameters: Dict[str, Any] = Field(
        default_factory=dict, description="Type-specific parameters"
    )
    examples: List[str] = Field(default_factory=list, description="Usage examples")


class RelationshipGenerationRequest(MOABaseModel):
    """Request model for relationship generation."""

    memory_ids: Optional[List[str]] = Field(
        None, description="Specific memory IDs to process"
    )
    force_regenerate: bool = Field(
        False, description="Force regeneration of existing relationships"
    )
    batch_size: int = Field(10, ge=1, le=50, description="Processing batch size")


class RelationshipGenerationResponse(MOABaseModel):
    """Response model for relationship generation."""

    status: str = Field(..., description="Generation status")
    message: str = Field(..., description="Status message")
    stats: Dict[str, int] = Field(..., description="Generation statistics")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")


class RelationshipStats(MOABaseModel):
    """Relationship statistics model."""

    total_relationships: int = Field(..., description="Total number of relationships")
    relationship_types: Dict[str, int] = Field(
        ..., description="Count by relationship type"
    )
    average_strength: float = Field(..., description="Average relationship strength")
    strongest_relationships: List[GraphRelationship] = Field(
        default_factory=list, description="Strongest relationships"
    )
    weakest_relationships: List[GraphRelationship] = Field(
        default_factory=list, description="Weakest relationships"
    )
    graph_density: float = Field(..., description="Graph density metric")
    connected_components: int = Field(..., description="Number of connected components")


class CleanupRelationshipsResponse(MOABaseModel):
    """Response model for relationship cleanup operations."""

    status: str = Field(..., description="Cleanup status")
    removed_count: int = Field(..., description="Number of relationships removed")
    remaining_count: int = Field(..., description="Number of relationships remaining")
    cleanup_criteria: Dict[str, Any] = Field(..., description="Cleanup criteria used")
    execution_time_ms: int = Field(
        ..., description="Cleanup execution time in milliseconds"
    )
