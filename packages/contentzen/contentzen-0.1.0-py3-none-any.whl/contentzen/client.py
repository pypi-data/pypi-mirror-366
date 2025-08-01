import requests
from typing import Optional, Dict, Any
from .exceptions import ContentZenError, AuthenticationError, NotFoundError, APIError

class ContentZenClient:
    """
    Official Python SDK client for ContentZen headless CMS.
    Handles both public and private (API token) endpoints.
    """
    BASE_URL = "https://api.contentzen.io"

    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize the ContentZenClient.
        :param api_token: API token for private endpoints (optional for public endpoints)
        """
        self.api_token = api_token

    def _headers(self) -> Dict[str, str]:
        headers = {}
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"
        return headers

    def _handle_response(self, resp):
        if 200 <= resp.status_code < 300:
            # Success
            if resp.content:
                try:
                    return resp.json()
                except Exception:
                    return resp.content
            return None
        elif resp.status_code in (401, 403):
            raise AuthenticationError(f"Authentication failed: {resp.text}")
        elif resp.status_code == 404:
            raise NotFoundError(f"Resource not found: {resp.text}")
        else:
            raise APIError(f"API error {resp.status_code}: {resp.text}")

    # ------------------- Public API Methods (No Auth) -------------------

    def get_public_documents(self, collection_uuid: str, limit: int = 10, offset: int = 0, state: str = "published") -> Any:
        """
        Get all published documents from a public collection.
        """
        url = f"{self.BASE_URL}/api/v1/documents/collection/{collection_uuid}"
        params = {"limit": limit, "offset": offset, "state": state}
        resp = requests.get(url, params=params)
        return self._handle_response(resp)

    def get_public_document(self, collection_uuid: str, document_uuid: str) -> Any:
        """
        Get a specific document from a public collection.
        """
        url = f"{self.BASE_URL}/api/v1/documents/collection/{collection_uuid}/{document_uuid}"
        resp = requests.get(url)
        return self._handle_response(resp)

    # ------------------- Private API Methods (API Token Required) -------------------

    def get_documents(self, collection_uuid: str, limit: int = 10, offset: int = 0) -> Any:
        """
        Get documents from a collection (API token required).
        """
        url = f"{self.BASE_URL}/api/v1/documents/{collection_uuid}"
        headers = self._headers()
        params = {"limit": limit, "offset": offset}
        resp = requests.get(url, headers=headers, params=params)
        return self._handle_response(resp)

    def get_document(self, collection_uuid: str, document_uuid: str) -> Any:
        """
        Get a specific document from a collection (API token required).
        """
        url = f"{self.BASE_URL}/api/v1/documents/{collection_uuid}/{document_uuid}"
        headers = self._headers()
        resp = requests.get(url, headers=headers)
        return self._handle_response(resp)

    def create_document(self, collection_uuid: str, payload: dict, lang: str = "en", state: str = "draft") -> Any:
        """
        Create a new document in a collection (API token required).
        :param collection_uuid: UUID of the collection
        :param payload: Document data (dict)
        :param lang: Language code (default: 'en')
        :param state: Document state (default: 'draft')
        """
        url = f"{self.BASE_URL}/api/v1/documents/{collection_uuid}"
        headers = self._headers()
        headers["Content-Type"] = "application/json"
        data = {
            "payload": payload,
            "lang": lang,
            "state": state
        }
        resp = requests.post(url, headers=headers, json=data)
        return self._handle_response(resp)

    def update_document(self, collection_uuid: str, document_uuid: str, payload: dict, state: str = "published") -> Any:
        """
        Update an existing document in a collection (API token required).
        :param collection_uuid: UUID of the collection
        :param document_uuid: UUID of the document
        :param payload: Updated document data (dict)
        :param state: Document state (default: 'published')
        """
        url = f"{self.BASE_URL}/api/v1/documents/{collection_uuid}/{document_uuid}"
        headers = self._headers()
        headers["Content-Type"] = "application/json"
        data = {
            "payload": payload,
            "state": state
        }
        resp = requests.put(url, headers=headers, json=data)
        return self._handle_response(resp)

    def delete_document(self, collection_uuid: str, document_uuid: str) -> Any:
        """
        Delete a document from a collection (API token required).
        :param collection_uuid: UUID of the collection
        :param document_uuid: UUID of the document
        """
        url = f"{self.BASE_URL}/api/v1/documents/{collection_uuid}/{document_uuid}"
        headers = self._headers()
        resp = requests.delete(url, headers=headers)
        return self._handle_response(resp)

    def get_collections(self) -> Any:
        """
        Get all collections for a project (API token required).
        """
        url = f"{self.BASE_URL}/api/v1/collections"
        headers = self._headers()
        resp = requests.get(url, headers=headers)
        return self._handle_response(resp)

    def get_collection(self, collection_uuid: str) -> Any:
        """
        Get a specific collection (API token required).
        """
        url = f"{self.BASE_URL}/api/v1/collections/{collection_uuid}"
        headers = self._headers()
        resp = requests.get(url, headers=headers)
        return self._handle_response(resp)

    def create_collection(self, name: str, display_name: str, description: str, is_public: bool, fields: list) -> Any:
        """
        Create a new collection (API token required).
        :param name: Collection name (str)
        :param display_name: Display name (str)
        :param description: Description (str)
        :param is_public: Whether the collection is public (bool)
        :param fields: List of field definitions (list of dict)
        """
        url = f"{self.BASE_URL}/api/v1/collections"
        headers = self._headers()
        headers["Content-Type"] = "application/json"
        data = {
            "name": name,
            "display_name": display_name,
            "description": description,
            "is_public": is_public,
            "fields": fields
        }
        resp = requests.post(url, headers=headers, json=data)
        return self._handle_response(resp)

    def update_collection(self, collection_uuid: str, display_name: str, description: str, is_public: bool, fields: list) -> Any:
        """
        Update a collection (API token required).
        :param collection_uuid: UUID of the collection
        :param display_name: New display name (str)
        :param description: New description (str)
        :param is_public: Whether the collection is public (bool)
        :param fields: List of field definitions (list of dict)
        """
        url = f"{self.BASE_URL}/api/v1/collections/{collection_uuid}"
        headers = self._headers()
        headers["Content-Type"] = "application/json"
        data = {
            "display_name": display_name,
            "description": description,
            "is_public": is_public,
            "fields": fields
        }
        resp = requests.put(url, headers=headers, json=data)
        return self._handle_response(resp)

    def delete_collection(self, collection_uuid: str) -> Any:
        """
        Delete a collection (API token required).
        :param collection_uuid: UUID of the collection
        """
        url = f"{self.BASE_URL}/api/v1/collections/{collection_uuid}"
        headers = self._headers()
        resp = requests.delete(url, headers=headers)
        return self._handle_response(resp)

    def get_collection_schema(self, collection_uuid: str) -> Any:
        """
        Get collection schema (API token required).
        :param collection_uuid: UUID of the collection
        """
        url = f"{self.BASE_URL}/api/v1/collections/{collection_uuid}/schema"
        headers = self._headers()
        resp = requests.get(url, headers=headers)
        return self._handle_response(resp)

    def get_collection_fields(self, collection_uuid: str) -> Any:
        """
        Get collection fields (API token required).
        :param collection_uuid: UUID of the collection
        """
        url = f"{self.BASE_URL}/api/v1/collections/{collection_uuid}/fields"
        headers = self._headers()
        resp = requests.get(url, headers=headers)
        return self._handle_response(resp)

    def get_field_types(self) -> Any:
        """
        Get available field types (API token required).
        """
        url = f"{self.BASE_URL}/api/v1/collections/field-types"
        headers = self._headers()
        resp = requests.get(url, headers=headers)
        return self._handle_response(resp)

    def list_media(self) -> Any:
        """
        List all media files (API token required).
        """
        url = f"{self.BASE_URL}/api/v1/media/ls"
        headers = self._headers()
        resp = requests.get(url, headers=headers)
        return self._handle_response(resp)

    def upload_media(self, file_path: str) -> Any:
        """
        Upload a media file (API token required).
        :param file_path: Path to the file to upload
        """
        url = f"{self.BASE_URL}/api/v1/media/upload"
        headers = self._headers()
        with open(file_path, 'rb') as f:
            files = {'file': f}
            resp = requests.post(url, headers=headers, files=files)
        return self._handle_response(resp)

    def get_media_file(self, media_uuid: str) -> Any:
        """
        Get specific media file details (API token required).
        :param media_uuid: UUID of the media file
        """
        url = f"{self.BASE_URL}/api/v1/media/{media_uuid}"
        headers = self._headers()
        resp = requests.get(url, headers=headers)
        return self._handle_response(resp)

    def update_media(self, media_uuid: str, alt_text: str) -> Any:
        """
        Update media file metadata (API token required).
        :param media_uuid: UUID of the media file
        :param alt_text: New alt text for the media file
        """
        url = f"{self.BASE_URL}/api/v1/media/{media_uuid}"
        headers = self._headers()
        headers["Content-Type"] = "application/json"
        data = {"alt_text": alt_text}
        resp = requests.put(url, headers=headers, json=data)
        return self._handle_response(resp)

    def delete_media(self, media_uuid: str) -> Any:
        """
        Delete a media file (API token required).
        :param media_uuid: UUID of the media file
        """
        url = f"{self.BASE_URL}/api/v1/media/{media_uuid}"
        headers = self._headers()
        resp = requests.delete(url, headers=headers)
        return self._handle_response(resp)

    def download_media(self, media_uuid: str, dest_path: str) -> None:
        """
        Download a media file (API token required).
        :param media_uuid: UUID of the media file
        :param dest_path: Path to save the downloaded file
        """
        url = f"{self.BASE_URL}/api/v1/media/{media_uuid}/download"
        headers = self._headers()
        resp = requests.get(url, headers=headers, stream=True)
        if not (200 <= resp.status_code < 300):
            self._handle_response(resp)
        with open(dest_path, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

    def list_webhooks(self) -> Any:
        """
        List all webhooks (API token required).
        """
        url = f"{self.BASE_URL}/api/v1/webhooks"
        headers = self._headers()
        resp = requests.get(url, headers=headers)
        return self._handle_response(resp)

    def create_webhook(self, name: str, url_: str, events: list, method: str = "POST") -> Any:
        """
        Create a new webhook (API token required).
        :param name: Webhook name (str)
        :param url_: Target URL for the webhook (str)
        :param events: List of event names (list of str)
        :param method: HTTP method for webhook (default: 'POST')
        """
        url = f"{self.BASE_URL}/api/v1/webhooks"
        headers = self._headers()
        headers["Content-Type"] = "application/json"
        data = {
            "name": name,
            "url": url_,
            "events": events,
            "method": method
        }
        resp = requests.post(url, headers=headers, json=data)
        return self._handle_response(resp)

    def update_webhook(self, webhook_uuid: str, name: str, url_: str, events: list, method: str = "POST") -> Any:
        """
        Update a webhook (API token required).
        :param webhook_uuid: UUID of the webhook
        :param name: Webhook name (str)
        :param url_: Target URL for the webhook (str)
        :param events: List of event names (list of str)
        :param method: HTTP method for webhook (default: 'POST')
        """
        url = f"{self.BASE_URL}/api/v1/webhooks/{webhook_uuid}"
        headers = self._headers()
        headers["Content-Type"] = "application/json"
        data = {
            "name": name,
            "url": url_,
            "events": events,
            "method": method
        }
        resp = requests.put(url, headers=headers, json=data)
        return self._handle_response(resp)

    def delete_webhook(self, webhook_uuid: str) -> Any:
        """
        Delete a webhook (API token required).
        :param webhook_uuid: UUID of the webhook
        """
        url = f"{self.BASE_URL}/api/v1/webhooks/{webhook_uuid}"
        headers = self._headers()
        resp = requests.delete(url, headers=headers)
        return self._handle_response(resp)