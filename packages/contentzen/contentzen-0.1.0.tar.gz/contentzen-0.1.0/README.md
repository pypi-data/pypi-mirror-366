# ContentZen Python SDK

Official Python SDK for interacting with ContentZen headless CMS.

## Features
- Access public and private ContentZen API endpoints
- Full CRUD for documents, collections, media, and webhooks
- Automatic API token authentication
- Custom exceptions for robust error handling
- Simple, Pythonic interface

## Installation

```bash
pip install contentzen  # (when published)
```

## Authentication

Some endpoints require an API token. You can obtain your API token after registering at [contentzen.io](https://contentzen.io).

## Usage

### Public Endpoints (No Auth Required)

```python
from contentzen import ContentZenClient

client = ContentZenClient()
public_docs = client.get_public_documents(collection_uuid="your-collection-uuid")
public_doc = client.get_public_document(collection_uuid="your-collection-uuid", document_uuid="your-document-uuid")
```

### Private Endpoints (API Token Required)

```python
from contentzen import ContentZenClient
client = ContentZenClient(api_token="your_api_token")
```

#### Documents
```python
docs = client.get_documents(collection_uuid="your-collection-uuid")
doc = client.get_document(collection_uuid="your-collection-uuid", document_uuid="your-document-uuid")
new_doc = client.create_document(collection_uuid="your-collection-uuid", payload={"title": "New Post", "content": "..."})
updated_doc = client.update_document(collection_uuid="your-collection-uuid", document_uuid="your-document-uuid", payload={"title": "Updated"})
client.delete_document(collection_uuid="your-collection-uuid", document_uuid="your-document-uuid")
```

#### Collections
```python
collections = client.get_collections()
collection = client.get_collection(collection_uuid="your-collection-uuid")
created = client.create_collection(
    name="products",
    display_name="Products",
    description="Product catalog",
    is_public=False,
    fields=[{"name": "title", "type": "string", "display_name": "Title", "required": True}]
)
updated = client.update_collection(
    collection_uuid="your-collection-uuid",
    display_name="Updated Products",
    description="Updated description",
    is_public=True,
    fields=[{"name": "title", "type": "string", "display_name": "Title", "required": True}]
)
client.delete_collection(collection_uuid="your-collection-uuid")
schema = client.get_collection_schema(collection_uuid="your-collection-uuid")
fields = client.get_collection_fields(collection_uuid="your-collection-uuid")
field_types = client.get_field_types()
```

#### Media
```python
media_list = client.list_media()
media = client.get_media_file(media_uuid="your-media-uuid")
client.upload_media(file_path="/path/to/file.jpg")
client.update_media(media_uuid="your-media-uuid", alt_text="New alt text")
client.delete_media(media_uuid="your-media-uuid")
client.download_media(media_uuid="your-media-uuid", dest_path="/tmp/file.jpg")
```

#### Webhooks
```python
webhooks = client.list_webhooks()
created = client.create_webhook(
    name="My Webhook",
    url_="https://example.com/webhook",
    events=["document.created", "document.updated"]
)
updated = client.update_webhook(
    webhook_uuid="your-webhook-uuid",
    name="Updated Webhook",
    url_="https://example.com/webhook",
    events=["document.created", "document.updated", "document.deleted"]
)
client.delete_webhook(webhook_uuid="your-webhook-uuid")
```

## Error Handling
All methods raise custom exceptions on errors:
- `AuthenticationError`: Invalid or missing API token
- `NotFoundError`: Resource not found (404)
- `APIError`: Other API errors
- `ContentZenError`: Base exception

Example:
```python
from contentzen import ContentZenClient
from contentzen.exceptions import AuthenticationError, NotFoundError, APIError

client = ContentZenClient(api_token="invalid")
try:
    docs = client.get_documents(collection_uuid="...")
except AuthenticationError:
    print("Invalid API token!")
except NotFoundError:
    print("Resource not found!")
except APIError as e:
    print(f"API error: {e}")
```

## Troubleshooting
- Ensure your API token is valid and has the correct permissions
- Check that UUIDs for collections, documents, media, and webhooks are correct
- For file uploads/downloads, verify file paths and permissions

## License

MIT