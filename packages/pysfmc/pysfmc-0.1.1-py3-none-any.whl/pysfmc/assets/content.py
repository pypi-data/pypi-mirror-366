"""Content client for SFMC Assets (Content Builder) API."""

from typing import TYPE_CHECKING, Any

from ..models.assets import Asset, AssetTypeCreate, CreateAsset

if TYPE_CHECKING:
    from ..client import AsyncSFMCClient, SFMCClient


class ContentClient:
    """Synchronous client for Content Builder asset content operations."""

    def __init__(self, client: "SFMCClient"):
        self._client = client

    def create_asset(
        self,
        name: str,
        content_type: str,
        asset_type_name: str,
        asset_type_id: int,
        customer_key: str,
        description: str | None = None,
        content: str | None = None,
        design: str | None = None,
        super_content: str | None = None,
        tags: list[str] | None = None,
        category_id: int | None = None,
        data: dict[str, Any] | None = None,
        meta: dict[str, Any] | None = None,
        custom_fields: dict[str, Any] | None = None,
        views: dict[str, Any] | None = None,
        channels: dict[str, bool] | None = None,
        slots: dict[str, Any] | None = None,
        blocks: dict[str, Any] | None = None,
        template: dict[str, Any] | None = None,
        file_properties: dict[str, Any] | None = None,
        **kwargs,
    ) -> Asset:
        """Create a new asset in Content Builder.

        Args:
            name: Asset name (required, max 200 characters)
            content_type: Type of content attribute (required)
            asset_type_name: Asset type name (required, e.g., 'htmlemail')
            asset_type_id: Asset type ID (required)
            customer_key: Reference to customer's private ID/name (required)
            description: Asset description
            content: Asset content
            design: Asset design
            super_content: Asset super content
            tags: List of asset tags
            category_id: Category ID for the asset
            data: Asset data object
            meta: Asset metadata
            custom_fields: Custom field data
            views: Asset views (email template slots, etc.)
            channels: Channel configuration (email, web, mobile)
            slots: Asset slots
            blocks: Asset blocks
            template: Template information
            file_properties: File properties for file-based assets
            **kwargs: Additional fields supported by CreateAsset model

        Returns:
            Asset model instance of the created asset

        Raises:
            SFMCValidationError: If required fields are missing
            SFMCPermissionError: If insufficient permissions
            SFMCAPIError: For other API errors
        """
        # Create CreateAsset object with proper validation
        create_asset = CreateAsset(
            name=name,
            content_type=content_type,
            customer_key=customer_key,
            asset_type=AssetTypeCreate(name=asset_type_name, id=asset_type_id),
            description=description,
            content=content,
            design=design,
            super_content=super_content,
            tags=tags,
            category={"id": category_id} if category_id is not None else None,
            data=data,
            meta=meta,
            custom_fields=custom_fields,
            views=views,
            channels=channels,
            slots=slots,
            blocks=blocks,
            template=template,
            file_properties=file_properties,
            **kwargs,
        )

        # Make the API call with the CreateAsset model
        # (will be serialized with proper aliases)
        response_data = self._client.post("/asset/v1/content/assets", json=create_asset)
        return Asset(**response_data)


class AsyncContentClient:
    """Asynchronous client for Content Builder asset content operations."""

    def __init__(self, client: "AsyncSFMCClient"):
        self._client = client

    async def create_asset(
        self,
        name: str,
        content_type: str,
        asset_type_name: str,
        asset_type_id: int,
        customer_key: str,
        description: str | None = None,
        content: str | None = None,
        design: str | None = None,
        super_content: str | None = None,
        tags: list[str] | None = None,
        category_id: int | None = None,
        data: dict[str, Any] | None = None,
        meta: dict[str, Any] | None = None,
        custom_fields: dict[str, Any] | None = None,
        views: dict[str, Any] | None = None,
        channels: dict[str, bool] | None = None,
        slots: dict[str, Any] | None = None,
        blocks: dict[str, Any] | None = None,
        template: dict[str, Any] | None = None,
        file_properties: dict[str, Any] | None = None,
        **kwargs,
    ) -> Asset:
        """Create a new asset in Content Builder.

        Args:
            name: Asset name (required, max 200 characters)
            content_type: Type of content attribute (required)
            asset_type_name: Asset type name (required, e.g., 'htmlemail')
            asset_type_id: Asset type ID (required)
            customer_key: Reference to customer's private ID/name (required)
            description: Asset description
            content: Asset content
            design: Asset design
            super_content: Asset super content
            tags: List of asset tags
            category_id: Category ID for the asset
            data: Asset data object
            meta: Asset metadata
            custom_fields: Custom field data
            views: Asset views (email template slots, etc.)
            channels: Channel configuration (email, web, mobile)
            slots: Asset slots
            blocks: Asset blocks
            template: Template information
            file_properties: File properties for file-based assets
            **kwargs: Additional fields supported by CreateAsset model

        Returns:
            Asset model instance of the created asset

        Raises:
            SFMCValidationError: If required fields are missing
            SFMCPermissionError: If insufficient permissions
            SFMCAPIError: For other API errors
        """
        # Create CreateAsset object with proper validation
        create_asset = CreateAsset(
            name=name,
            content_type=content_type,
            customer_key=customer_key,
            asset_type=AssetTypeCreate(name=asset_type_name, id=asset_type_id),
            description=description,
            content=content,
            design=design,
            super_content=super_content,
            tags=tags,
            category={"id": category_id} if category_id is not None else None,
            data=data,
            meta=meta,
            custom_fields=custom_fields,
            views=views,
            channels=channels,
            slots=slots,
            blocks=blocks,
            template=template,
            file_properties=file_properties,
            **kwargs,
        )

        # Make the API call with the CreateAsset model
        # (will be serialized with proper aliases)
        response_data = await self._client.post(
            "/asset/v1/content/assets", json=create_asset
        )
        return Asset(**response_data)
