"""Relationships API operations for MOA SDK."""

from typing import Any, Dict, List, Union

from ..models.graph import (
    CleanupRelationshipsResponse,
    RelationshipGenerationRequest,
    RelationshipGenerationResponse,
    RelationshipStats,
)
from ..utils.http import HTTPClient


class RelationshipsAPI:
    """Relationships operations API client."""

    def __init__(self, http_client: HTTPClient):
        """Initialize Relationships API client."""
        self.http = http_client

    def generate_relationships(
        self, request: Union[RelationshipGenerationRequest, Dict[str, Any]]
    ) -> RelationshipGenerationResponse:
        """Generate relationships between memories using AI analysis.

        This method analyzes memories and automatically creates relationships based on:
        - Semantic similarity
        - Temporal proximity
        - Shared concepts
        - Keyword co-occurrence
        - Content analysis

        Args:
            request: Relationship generation request data

        Returns:
            RelationshipGenerationResponse: Generation response
        """
        if isinstance(request, dict):
            request_data = request
        else:
            request_data = request.dict(exclude_unset=True)

        response_data = self.http.post("relationships/generate", json_data=request_data)
        return RelationshipGenerationResponse(**response_data)

    async def agenerate_relationships(
        self, request: Union[RelationshipGenerationRequest, Dict[str, Any]]
    ) -> RelationshipGenerationResponse:
        """Async generate relationships between memories using AI analysis."""
        if isinstance(request, dict):
            request_data = request
        else:
            request_data = request.dict(exclude_unset=True)

        response_data = await self.http.apost(
            "relationships/generate", json_data=request_data
        )
        return RelationshipGenerationResponse(**response_data)

    def generate_all_relationships(
        self, force_regenerate: bool = False, batch_size: int = 10
    ) -> RelationshipGenerationResponse:
        """Generate relationships for all memories.

        Args:
            force_regenerate: Force regeneration of existing relationships
            batch_size: Processing batch size

        Returns:
            RelationshipGenerationResponse: Generation response
        """
        request = RelationshipGenerationRequest(
            memory_ids=None,  # None means all memories
            force_regenerate=force_regenerate,
            batch_size=batch_size,
        )
        return self.generate_relationships(request)

    async def agenerate_all_relationships(
        self, force_regenerate: bool = False, batch_size: int = 10
    ) -> RelationshipGenerationResponse:
        """Async generate relationships for all memories."""
        request = RelationshipGenerationRequest(
            memory_ids=None,  # None means all memories
            force_regenerate=force_regenerate,
            batch_size=batch_size,
        )
        return await self.agenerate_relationships(request)

    def generate_relationships_for_memories(
        self,
        memory_ids: List[str],
        force_regenerate: bool = False,
        batch_size: int = 10,
    ) -> RelationshipGenerationResponse:
        """Generate relationships for specific memories.

        Args:
            memory_ids: List of memory IDs to process
            force_regenerate: Force regeneration of existing relationships
            batch_size: Processing batch size

        Returns:
            RelationshipGenerationResponse: Generation response
        """
        request = RelationshipGenerationRequest(
            memory_ids=memory_ids,
            force_regenerate=force_regenerate,
            batch_size=batch_size,
        )
        return self.generate_relationships(request)

    async def agenerate_relationships_for_memories(
        self,
        memory_ids: List[str],
        force_regenerate: bool = False,
        batch_size: int = 10,
    ) -> RelationshipGenerationResponse:
        """Async generate relationships for specific memories."""
        request = RelationshipGenerationRequest(
            memory_ids=memory_ids,
            force_regenerate=force_regenerate,
            batch_size=batch_size,
        )
        return await self.agenerate_relationships(request)

    def get_relationship_stats(self) -> RelationshipStats:
        """Get statistics about relationships in the workspace.

        Returns:
            RelationshipStats: Relationship statistics
        """
        response_data = self.http.get("relationships/stats")
        return RelationshipStats(**response_data)

    async def aget_relationship_stats(self) -> RelationshipStats:
        """Async get statistics about relationships in the workspace."""
        response_data = await self.http.aget("relationships/stats")
        return RelationshipStats(**response_data)

    def cleanup_relationships(
        self, min_strength: float = 0.1
    ) -> CleanupRelationshipsResponse:
        """Clean up weak or redundant relationships.

        Args:
            min_strength: Minimum relationship strength to keep

        Returns:
            CleanupRelationshipsResponse: Cleanup response
        """
        params = {"min_strength": min_strength}
        response_data = self.http.delete("relationships/cleanup", params=params)
        return CleanupRelationshipsResponse(**response_data)

    async def acleanup_relationships(
        self, min_strength: float = 0.1
    ) -> CleanupRelationshipsResponse:
        """Async clean up weak or redundant relationships."""
        params = {"min_strength": min_strength}
        response_data = await self.http.adelete("relationships/cleanup", params=params)
        return CleanupRelationshipsResponse(**response_data)

    def cleanup_weak_relationships(
        self, min_strength: float = 0.3
    ) -> CleanupRelationshipsResponse:
        """Clean up relationships below a strength threshold.

        Args:
            min_strength: Minimum relationship strength to keep

        Returns:
            CleanupRelationshipsResponse: Cleanup response
        """
        return self.cleanup_relationships(min_strength=min_strength)

    async def acleanup_weak_relationships(
        self, min_strength: float = 0.3
    ) -> CleanupRelationshipsResponse:
        """Async clean up relationships below a strength threshold."""
        return await self.acleanup_relationships(min_strength=min_strength)

    def optimize_graph(
        self,
        regenerate_relationships: bool = False,
        cleanup_threshold: float = 0.1,
        batch_size: int = 10,
    ) -> Dict[str, Any]:
        """Optimize the relationship graph by regenerating and cleaning up.

        Args:
            regenerate_relationships: Whether to regenerate relationships
            cleanup_threshold: Minimum strength threshold for cleanup
            batch_size: Batch size for relationship generation

        Returns:
            Dict containing both generation and cleanup results
        """
        results = {}

        if regenerate_relationships:
            generation_result = self.generate_all_relationships(
                force_regenerate=True, batch_size=batch_size
            )
            results["generation"] = generation_result.dict()

        cleanup_result = self.cleanup_relationships(min_strength=cleanup_threshold)
        results["cleanup"] = cleanup_result.dict()

        stats = self.get_relationship_stats()
        results["final_stats"] = stats.dict()

        return results

    async def aoptimize_graph(
        self,
        regenerate_relationships: bool = False,
        cleanup_threshold: float = 0.1,
        batch_size: int = 10,
    ) -> Dict[str, Any]:
        """Async optimize the relationship graph by regenerating and cleaning up."""
        results = {}

        if regenerate_relationships:
            generation_result = await self.agenerate_all_relationships(
                force_regenerate=True, batch_size=batch_size
            )
            results["generation"] = generation_result.dict()

        cleanup_result = await self.acleanup_relationships(
            min_strength=cleanup_threshold
        )
        results["cleanup"] = cleanup_result.dict()

        stats = await self.aget_relationship_stats()
        results["final_stats"] = stats.dict()

        return results
