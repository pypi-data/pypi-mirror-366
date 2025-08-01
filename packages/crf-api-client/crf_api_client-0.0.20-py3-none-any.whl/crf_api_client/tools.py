# ruff: noqa: E501, SLF001
import logging
from abc import ABC, abstractmethod
from typing import Callable, Optional

import requests

# Configure logging
logger = logging.getLogger(__name__)


class Tool(ABC):
    """Base class for all tools"""

    def set_assistant(self, assistant):
        """Set the assistant for the tool"""
        self.assistant = assistant

    def log_tool_call(self, results, tool_params):
        """Process the results of the tool in a standardized way."""
        self.assistant.log_tool_call(
            tool_name=self.tool_name,
            params=tool_params,
            results=results,
        )
        return results

    @abstractmethod
    def tool_function(self) -> Callable:
        """Get the tool function itself. This must be overriden in the child class."""


class SemanticSearchTool(Tool):
    def retrieve_with_semantic_search(self):
        return self.assistant.warehouse.retrieve_with_semantic_search(
            query=self.query,
            n_objects=self.top_k or self.default_top_k,
            indexes=self.indexes,
            enrich_with_chunks=self.enriched_with_chunks,
            included_tags=self.included_tags,
            excluded_tags=self.excluded_tags,
        )

    def endpoint(self):
        return f"{self.assistant.crf_client.base_url}/api/v1/projects/{self.assistant.project_id}/retrieve-with-naive/"

    def finalize(self, results):
        self.assistant.store_in_cache(results)
        return self.log_tool_call(
            results=results, tool_params={"query": self.query, "top_k": self.top_k}
        )


class SemanticSearchOnChunksTool(SemanticSearchTool):
    tool_name = "semantic_search_on_chunks"
    tool_description = "Search inside the chunks collection from Knowledge Warehouse for information that would be relevant to the current question."

    def __init__(self, included_tags: list = [], excluded_tags: list = [], default_top_k: int = 5):
        self.included_tags = included_tags
        self.excluded_tags = excluded_tags
        self.enriched_with_chunks = False
        self.default_top_k = default_top_k

    def tool_function(self) -> Callable:
        return self._semantic_search_on_chunks

    def _semantic_search_on_chunks(self, query: str, top_k: Optional[int] = None) -> list:
        """Search inside the chunks collection from Knowledge Warehouse"""
        self.query = query
        self.top_k = top_k
        self.indexes = ["chunks"]
        retrieval_results = self.retrieve_with_semantic_search()
        fields_to_keep = [
            "chunk_ids",
            "type",
            "content",
            "name",
            "document_id",
            "reference_url",
            "score",
        ]
        results = []
        for result in retrieval_results:
            result_dict = {k: result[k] for k in fields_to_keep if k in result}
            if "chunk_ids" in result:
                result_dict["uuid"] = result["chunk_ids"][0]
            results.append(result_dict)
        return self.finalize(results)


class SemanticSearchOnObjectsTool(SemanticSearchTool):
    tool_name = "semantic_search_on_objects"
    tool_description = "Search objects."

    def __init__(
        self,
        enriched_with_chunks: bool = False,
        included_tags: list = [],
        excluded_tags: list = [],
        default_top_k: int = 5,
    ):
        self.included_tags = included_tags
        self.excluded_tags = excluded_tags
        self.enriched_with_chunks = enriched_with_chunks
        self.default_top_k = default_top_k

    def tool_function(self) -> Callable:
        return self._semantic_search_on_objects_enriched_with_chunks

    def _semantic_search_on_objects_enriched_with_chunks(
        self, query: str, top_k: Optional[int] = None
    ):
        """Search inside the objects collection from Knowledge Warehouse"""
        self.query = query
        self.top_k = top_k
        self.indexes = ["objects"]
        results = self.retrieve_with_semantic_search()
        for result in results:
            if "object_id" in result:
                result["uuid"] = result["object_id"]
        return self.finalize(results)


class StructuredQueryTool(Tool):
    tool_name = "structured_query"
    tool_description = (
        "Create a graph query from the user query and run it on the Knowledge Warehouse Graph."
    )

    def tool_function(self) -> Callable:
        return self._structured_query

    def _structured_query(self, query: str):
        """Create a graph query from the user query and run it on the Knowledge Warehouse Graph."""
        response = requests.post(
            f"{self.assistant.crf_client.base_url}/api/v1/projects/{self.assistant.project_id}/generate-cypher-query/",
            headers=self.assistant.crf_client._get_headers(),
            json={"user_instruction": query},
        )
        response.raise_for_status()
        cypher_query = response.json()["generated_cypher_query"]
        if not cypher_query:
            return self.log_tool_call(results=[], tool_params={"query": query})

        response = requests.post(
            f"{self.assistant.crf_client.base_url}/api/v1/projects/{self.assistant.project_id}/run-neo4j-query/",
            headers=self.assistant.crf_client._get_headers(),
            json={"cypher_query": cypher_query},
        )
        response.raise_for_status()
        results = response.json()["retrieval_results"]
        self.assistant.store_in_cache(results)
        return self.log_tool_call(results, {"query": query})
