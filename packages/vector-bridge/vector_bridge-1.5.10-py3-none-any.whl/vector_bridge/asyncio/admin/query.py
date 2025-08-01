from typing import Any, Dict

from vector_bridge import AsyncVectorBridgeClient
from vector_bridge.schema.queries import QueryResponse


class AsyncQueryAdmin:
    """Async admin client for vector query endpoints."""

    def __init__(self, client: AsyncVectorBridgeClient):
        self.client = client

    async def run_search_query(
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

        await self.client._ensure_session()

        url = f"{self.client.base_url}/v1/admin/vector-query/search/run"
        params = {"vector_schema": vector_schema, "integration_name": integration_name}
        headers = self.client._get_auth_headers()

        async with self.client.session.post(url, headers=headers, params=params, json=query_args) as response:
            result = await self.client._handle_response(response)
            return QueryResponse.model_validate(result)

    async def run_find_similar_query(
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

        await self.client._ensure_session()

        url = f"{self.client.base_url}/v1/admin/vector-query/find-similar/run"
        params = {"vector_schema": vector_schema, "integration_name": integration_name}
        headers = self.client._get_auth_headers()

        async with self.client.session.post(url, headers=headers, params=params, json=query_args) as response:
            result = await self.client._handle_response(response)
            return QueryResponse.model_validate(result)
