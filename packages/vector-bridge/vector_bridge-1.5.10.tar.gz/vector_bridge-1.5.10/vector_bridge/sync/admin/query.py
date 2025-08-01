from typing import Any, Dict

from vector_bridge import VectorBridgeClient
from vector_bridge.schema.queries import QueryResponse


class QueryAdmin:
    """Admin client for vector query endpoints."""

    def __init__(self, client: VectorBridgeClient):
        self.client = client

    def run_search_query(
        self,
        vector_schema: str,
        query_args: Dict[str, Any],
        integration_name: str = None,
    ) -> QueryResponse:
        """
        Run a vector search query.

        Args:
            vector_schema: The schema to be queried
            query_args: Query parameters
            integration_name: The name of the Integration

        Returns:
            Search results
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/vector-query/search/run"
        params = {"vector_schema": vector_schema, "integration_name": integration_name}

        headers = self.client._get_auth_headers()
        response = self.client.session.post(url, headers=headers, params=params, json=query_args)
        return QueryResponse.model_validate(self.client._handle_response(response))

    def run_find_similar_query(
        self,
        vector_schema: str,
        query_args: Dict[str, Any],
        integration_name: str = None,
    ) -> QueryResponse:
        """
        Run a vector similarity query.

        Args:
            vector_schema: The schema to be queried
            query_args: Query parameters {"uuid" <uuid of the chunk>}
            integration_name: The name of the Integration

        Returns:
            Search results
        """
        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/vector-query/find-similar/run"
        params = {"vector_schema": vector_schema, "integration_name": integration_name}

        headers = self.client._get_auth_headers()
        response = self.client.session.post(url, headers=headers, params=params, json=query_args)
        return QueryResponse.model_validate(self.client._handle_response(response))
