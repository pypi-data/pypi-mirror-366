from vector_bridge import VectorBridgeClient
from vector_bridge.schema.settings import Settings


class SettingsAdmin:
    """Admin client for settings endpoints."""

    def __init__(self, client: VectorBridgeClient):
        self.client = client

    def get_settings(self) -> Settings:
        """Get system settings."""
        url = f"{self.client.base_url}/v1/settings"
        headers = self.client._get_auth_headers()
        response = self.client.session.get(url, headers=headers)
        result = self.client._handle_response(response)
        return Settings.model_validate(result)
