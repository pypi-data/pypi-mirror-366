"""
CKAN integration for Upstream SDK.
"""

from datetime import datetime
import json
import logging
import os
from pathlib import Path
from typing import Any, BinaryIO, Dict, List, Optional, Union, cast

import requests
from upstream_api_client import GetStationResponse
from upstream_api_client.models.get_campaign_response import GetCampaignResponse

from .exceptions import APIError

logger = logging.getLogger(__name__)


def _serialize_for_json(value: Any, max_length: int = 30000) -> str:
    """
    Convert a value to a JSON-serializable string, with special handling for dates and size limits.

    Args:
        value: The value to serialize
        max_length: Maximum allowed length for the serialized string (default: 30000 to stay under Solr's 32766 limit)

    Returns:
        JSON-serializable string representation, truncated if necessary
    """
    if value is None:
        return ""
    elif isinstance(value, datetime):
        # Format datetime for Solr compatibility (ISO format without timezone suffix)
        # Solr expects format like: 2025-07-22T11:16:48Z
        return value.strftime('%Y-%m-%dT%H:%M:%SZ')
    elif isinstance(value, (dict, list)):
        try:
            serialized = json.dumps(value, default=str)
            if len(serialized) > max_length:
                # Truncate large objects to prevent Solr field size errors
                logger.warning(f"Truncating large value (length: {len(serialized)}) to fit Solr field size limit")
                return serialized[:max_length] + "... [TRUNCATED]"
            return serialized
        except (TypeError, ValueError):
            result = str(value)
            if len(result) > max_length:
                logger.warning(f"Truncating large string value (length: {len(result)}) to fit Solr field size limit")
                return result[:max_length] + "... [TRUNCATED]"
            return result
    else:
        result = str(value)
        if len(result) > max_length:
            logger.warning(f"Truncating large string value (length: {len(result)}) to fit Solr field size limit")
            return result[:max_length] + "... [TRUNCATED]"
        return result



class CKANIntegration:
    """
    Handles CKAN data portal integration.
    """

    def __init__(self, ckan_url: str, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize CKAN integration.

        Args:
            ckan_url: CKAN portal URL
            config: Additional CKAN configuration
        """
        self.ckan_url = ckan_url.rstrip("/")
        self.config = config or {}
        self.session = requests.Session()

        # Store timeout for use in individual requests
        self.timeout = self.config.get("timeout", 30)

        # Set up authentication if provided
        api_key = self.config.get("api_key")
        if api_key:
            self.session.headers.update({"Authorization": api_key})

        access_token = self.config.get("access_token")
        if access_token:
            self.session.headers.update({"Authorization": f"Bearer {access_token}"})

    def create_dataset(
        self,
        name: str,
        title: str,
        description: str = "",
        organization: Optional[str] = None,
        tags: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Create a new CKAN dataset.

        Args:
            name: Dataset name (URL-friendly)
            title: Dataset title
            description: Dataset description
            organization: Organization name
            tags: List of tags
            **kwargs: Additional dataset metadata

        Returns:
            Created dataset information
        """

        # Determine organization - use parameter or fall back to config
        owner_org = organization or self.config.get("ckan_organization")

        # Prepare dataset metadata
        dataset_data = {
            "name": name,
            "title": title,
            "notes": description,
            "tags": [{"name": tag} for tag in (tags or [])],
            **kwargs,
        }

        # Add owner_org if available
        if owner_org:
            dataset_data["owner_org"] = owner_org
        elif not name.startswith("test-"):
            # Only require organization for non-test datasets
            raise APIError("Organization is required for dataset creation. Please set CKAN_ORGANIZATION environment variable or pass organization parameter.")

        # Remove None values
        dataset_data = {k: v for k, v in dataset_data.items() if v is not None}

        try:
            response = self.session.post(
                f"{self.ckan_url}/api/3/action/package_create", json=dataset_data, timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()

            if not result.get("success"):
                raise APIError(f"CKAN dataset creation failed: {result.get('error')}")

            dataset = result["result"]
            logger.info(
                f"Created CKAN dataset: {dataset['name']} (ID: {dataset['id']})"
            )

            return cast(Dict[str, Any], dataset)

        except requests.exceptions.RequestException as e:
            raise APIError(f"Failed to create CKAN dataset: {e}")

    def get_dataset(self, dataset_id: str) -> Dict[str, Any]:
        """
        Get CKAN dataset by ID or name.

        Args:
            dataset_id: Dataset ID or name

        Returns:
            Dataset information
        """
        try:
            response = self.session.get(
                f"{self.ckan_url}/api/3/action/package_show", params={"id": dataset_id}, timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()

            if not result.get("success"):
                raise APIError(f"CKAN dataset retrieval failed: {result.get('error')}")

            return cast(Dict[str, Any], result["result"])

        except requests.exceptions.RequestException as e:
            if hasattr(e, "response") and e.response is not None and e.response.status_code == 404:
                raise APIError(f"CKAN dataset not found: {dataset_id}")
            raise APIError(f"Failed to get CKAN dataset: {e}")

    def update_dataset(
        self,
        dataset_id: str,
        dataset_metadata: Optional[Dict[str, Any]] = None,
        custom_tags: Optional[List[str]] = None,
        merge_extras: bool = True,
        merge_tags: bool = True,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Update CKAN dataset with enhanced metadata support.

        Args:
            dataset_id: Dataset ID or name
            dataset_metadata: Custom metadata to add to dataset extras
            custom_tags: Additional tags to add to the dataset
            merge_extras: If True, merge with existing extras; if False, replace them
            merge_tags: If True, merge with existing tags; if False, replace them
            **kwargs: Additional dataset fields to update

        Returns:
            Updated dataset information

        Examples:
            Basic update:
            >>> ckan.update_dataset("my-dataset", title="New Title")

            Update with custom metadata:
            >>> ckan.update_dataset(
            ...     "my-dataset",
            ...     dataset_metadata={"project_status": "completed", "final_report": "available"},
            ...     custom_tags=["completed", "final"]
            ... )

            Replace all extras and tags:
            >>> ckan.update_dataset(
            ...     "my-dataset",
            ...     dataset_metadata={"new_field": "value"},
            ...     custom_tags=["new-tag"],
            ...     merge_extras=False,
            ...     merge_tags=False
            ... )
        """
        # Get current dataset
        current_dataset = self.get_dataset(dataset_id)

        # Start with current dataset data and apply kwargs updates
        updated_data = {**current_dataset, **kwargs}

        # Handle custom dataset metadata (extras)
        if dataset_metadata:
            current_extras = current_dataset.get('extras', [])

            if merge_extras:
                # Merge with existing extras
                # Convert existing extras to dict for easier manipulation
                extras_dict = {extra['key']: extra['value'] for extra in current_extras}

                # Add/update with new metadata
                for key, value in dataset_metadata.items():
                    extras_dict[key] = _serialize_for_json(value)

                # Convert back to list format
                updated_data['extras'] = [{"key": k, "value": v} for k, v in extras_dict.items()]
            else:
                # Replace existing extras with only the new metadata
                updated_data['extras'] = [{"key": k, "value": _serialize_for_json(v)} for k, v in dataset_metadata.items()]

        # Handle custom tags
        if custom_tags is not None:
            current_tags = []
            if current_dataset.get('tags'):
                current_tags = [tag['name'] if isinstance(tag, dict) else tag for tag in current_dataset['tags']]

            if merge_tags:
                # Merge with existing tags (avoid duplicates)
                all_tags = list(set(current_tags + custom_tags))
            else:
                # Replace with only the new tags
                all_tags = custom_tags

            updated_data['tags'] = all_tags

        # Handle tags from kwargs (for backward compatibility)
        if "tags" in updated_data and updated_data["tags"]:
            tags = updated_data["tags"]
            # Ensure tags are in the correct format
            if isinstance(tags, list):
                if tags and isinstance(tags[0], str):
                    # Convert string tags to dict format for CKAN API
                    updated_data["tags"] = [{"name": tag} for tag in tags]
                elif tags and isinstance(tags[0], dict):
                    # Already in correct format
                    pass
            else:
                # Handle unexpected tag format
                updated_data["tags"] = []

        try:
            response = self.session.post(
                f"{self.ckan_url}/api/3/action/package_update", json=updated_data, timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()

            if not result.get("success"):
                error_details = result.get('error', {})
                raise APIError(f"CKAN dataset update failed: {error_details}")

            dataset = result["result"]
            logger.info(f"Updated CKAN dataset: {dataset['name']}")

            return cast(Dict[str, Any], dataset)

        except requests.exceptions.RequestException as e:
            # Log the response content for debugging
            error_msg = f"Failed to update CKAN dataset: {e}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_content = e.response.json()
                    error_msg += f" - Response: {error_content}"
                except:
                    error_msg += f" - Response text: {e.response.text[:500]}"
            raise APIError(error_msg)

    def delete_dataset(self, dataset_id: str) -> bool:
        """
        Delete CKAN dataset.

        Args:
            dataset_id: Dataset ID or name

        Returns:
            True if successful
        """
        try:
            response = self.session.post(
                f"{self.ckan_url}/api/3/action/package_delete", json={"id": dataset_id}, timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()

            if not result.get("success"):
                raise APIError(f"CKAN dataset deletion failed: {result.get('error')}")

            logger.info(f"Deleted CKAN dataset: {dataset_id}")
            return True

        except requests.exceptions.RequestException as e:
            raise APIError(f"Failed to delete CKAN dataset: {e}")

    def create_resource(
        self,
        dataset_id: str,
        name: str,
        url: Optional[str] = None,
        file_path: Optional[Union[str, Path]] = None,
        file_obj: Optional[BinaryIO] = None,
        resource_type: str = "data",
        format: str = "CSV",
        description: str = "",
        metadata: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Create a resource within a CKAN dataset.

        Args:
            dataset_id: Dataset ID or name
            name: Resource name
            url: Resource URL (for URL-based resources)
            file_path: Path to file to upload
            file_obj: File object to upload
            resource_type: Resource type
            format: Resource format
            description: Resource description
            **kwargs: Additional resource metadata

        Returns:
            Created resource information
        """
        resource_data = {
            "package_id": dataset_id,
            "name": name,
            "resource_type": resource_type,
            "format": format,
            "description": description,
            **kwargs,
        }

        # Add metadata fields directly to resource (not in extras array)
        if metadata:
            for meta_item in metadata:
                if isinstance(meta_item, dict) and "key" in meta_item and "value" in meta_item:
                    resource_data[meta_item["key"]] = meta_item["value"]

        # Handle file upload vs URL
        if file_path or file_obj:
            # File upload
            files: Dict[str, Any] = {}
            if file_path:
                file_path = Path(file_path)
                if not file_path.exists():
                    raise APIError(f"File not found: {file_path}")
                files["upload"] = (file_path.name, open(file_path, "rb"))
            elif file_obj:
                filename = getattr(file_obj, "name", "uploaded_file")
                if hasattr(filename, "split"):
                    filename = os.path.basename(filename)
                files["upload"] = (str(filename), file_obj)

            try:
                response = self.session.post(
                    f"{self.ckan_url}/api/3/action/resource_create",
                    data=resource_data,
                    files=files,
                    timeout=self.timeout
                )
                response.raise_for_status()
            finally:
                # Close file if we opened it
                if file_path and "upload" in files:
                    files["upload"][1].close()
        else:
            # URL-based resource
            if not url:
                raise APIError("Either url, file_path, or file_obj must be provided")
            resource_data["url"] = url
            response = self.session.post(
                f"{self.ckan_url}/api/3/action/resource_create", json=resource_data, timeout=self.timeout
            )
            response.raise_for_status()

        try:
            result = response.json()

            if not result.get("success"):
                raise APIError(f"CKAN resource creation failed: {result.get('error')}")

            resource = result["result"]
            logger.info(
                f"Created CKAN resource: {resource['name']} (ID: {resource['id']})"
            )

            return cast(Dict[str, Any], resource)

        except requests.exceptions.RequestException as e:
            raise APIError(f"Failed to create CKAN resource: {e}")

    def list_datasets(
        self,
        organization: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        List CKAN datasets.

        Args:
            organization: Filter by organization
            tags: Filter by tags
            limit: Maximum number of datasets to return
            offset: Number of datasets to skip

        Returns:
            List of dataset information
        """
        params: Dict[str, Union[int, str]] = {"rows": limit, "start": offset}

        # Build query
        query_parts = []

        if organization:
            query_parts.append(f'owner_org:"{organization}"')

        if tags:
            tag_query = " OR ".join([f'tags:"{tag}"' for tag in tags])
            query_parts.append(f"({tag_query})")

        if query_parts:
            params["q"] = " AND ".join(query_parts)

        try:
            response = self.session.get(
                f"{self.ckan_url}/api/3/action/package_search", params=params, timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()

            if not result.get("success"):
                raise APIError(f"CKAN dataset search failed: {result.get('error')}")

            return cast(List[Dict[str, Any]], result["result"]["results"])

        except requests.exceptions.RequestException as e:
            raise APIError(f"Failed to list CKAN datasets: {e}")

    def sanitize_title(self, title: str) -> str:
        """
        Sanitize a title to be used as a CKAN dataset title.
        """
        return title.replace(" ", "_").replace("-", "_")

    def publish_campaign(
        self,
        campaign_id: int,
        campaign_data: GetCampaignResponse,
        station_measurements: BinaryIO,
        station_sensors: BinaryIO,
        station_data: GetStationResponse,
        dataset_metadata: Optional[Dict[str, Any]] = None,
        resource_metadata: Optional[Dict[str, Any]] = None,
        custom_tags: Optional[List[str]] = None,
        auto_publish: bool = True,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Publish campaign data to CKAN with custom metadata support.

        Args:
            campaign_id: Campaign ID
            campaign_data: Campaign information
            station_measurements: BinaryIO stream of station measurements CSV
            station_sensors: BinaryIO stream of station sensors CSV
            station_data: Station information
            dataset_metadata: Custom metadata for the CKAN dataset (added to extras)
            resource_metadata: Custom metadata for CKAN resources
            custom_tags: Additional tags for the dataset
            auto_publish: Whether to automatically publish the dataset
            **kwargs: Additional CKAN parameters

        Returns:
            CKAN publication result
        """
        # Create dataset name from campaign
        dataset_name = f"upstream-campaign-{campaign_id}"
        dataset_title = campaign_data.name

        if campaign_data.description:
            description = campaign_data.description
        else:
            description = f"\nSensor Types: {', '.join(campaign_data.summary.sensor_types)}"

        # Prepare base tags
        base_tags = ["environmental", "sensors", "upstream"]
        if custom_tags:
            base_tags.extend(custom_tags)

        # Prepare base dataset extras (avoid storing large campaign object to prevent Solr field size limits)
        base_extras = [
            {"key": "source", "value": "Upstream Platform"},
            {"key": "data_type", "value": "environmental_sensor_data"},
            {"key": "campaign_id", "value": str(campaign_id)},
            {"key": "campaign_name", "value": campaign_data.name or ""},
            {"key": "campaign_description", "value": campaign_data.description or ""},
            {"key": "campaign_contact_name", "value": campaign_data.contact_name or ""},
            {"key": "campaign_contact_email", "value": campaign_data.contact_email or ""},
            {"key": "campaign_allocation", "value": campaign_data.allocation or ""},
        ]

        # Add custom dataset metadata to extras
        if dataset_metadata:
            for key, value in dataset_metadata.items():
                base_extras.append({"key": key, "value": _serialize_for_json(value)})

        # Prepare dataset metadata
        dataset_data = {
            "name": dataset_name,
            "title": dataset_title,
            "notes": description,
            "tags": base_tags,
            "extras": base_extras,
            **kwargs  # Allow additional dataset-level parameters
        }

        try:
            # Create or update dataset
            should_update = False
            try:
                dataset = self.get_dataset(dataset_name)
                should_update = True
            except APIError:
                should_update = False

            if should_update:
                dataset = self.update_dataset(dataset_name, **dataset_data)
            else:
                dataset = self.create_dataset(**dataset_data)

            # Add resources for different data types
            resources_created = []


            # Prepare base station metadata (avoid storing large sensor objects to prevent Solr field size limits)
            base_station_metadata = [
                {"key": "station_id", "value": str(station_data.id)},
                {"key": "station_name", "value": station_data.name or ""},
                {"key": "station_description", "value": station_data.description or ""},
                {"key": "station_contact_name", "value": station_data.contact_name or ""},
                {"key": "station_contact_email", "value": station_data.contact_email or ""},
                {"key": "station_active", "value": str(station_data.active)},
                {"key": "station_geometry", "value": _serialize_for_json(station_data.geometry)},
                {"key": "station_sensors_count", "value": str(len(station_data.sensors) if station_data.sensors else 0)},
                # {"key": "station_sensors_aliases", "value": _serialize_for_json([sensor.alias for sensor in station_data.sensors] if station_data.sensors else [])},
                # {"key": "station_sensors_units", "value": _serialize_for_json([sensor.units for sensor in station_data.sensors] if station_data.sensors else [])},
                # {"key": "station_sensors_variablename", "value": _serialize_for_json([sensor.variablename for sensor in station_data.sensors] if station_data.sensors else [])},
            ]

            # Add custom resource metadata
            if resource_metadata:
                for key, value in resource_metadata.items():
                    base_station_metadata.append({"key": key, "value": _serialize_for_json(value)})


            # Add sensors resource (file upload or URL)
            published_at = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
            sensors_resource = self.create_resource(
                dataset_id=dataset["id"],
                name=f"{station_data.name} - Sensors Configuration - {published_at}",
                file_obj=station_sensors,
                format="CSV",
                description="Sensor configuration and metadata",
                metadata=base_station_metadata,
            )
            resources_created.append(sensors_resource)

            # Add measurements resource (file upload or URL)
            measurements_resource = self.create_resource(
                    dataset_id=dataset["id"],
                    name=f"{station_data.name} - Measurement Data - {published_at}",
                    file_obj=station_measurements,
                    format="CSV",
                    description="Environmental sensor measurements",
                    metadata=base_station_metadata,
                )
            resources_created.append(measurements_resource)

            # Publish dataset if requested
            if auto_publish and not dataset.get("private", True):
                self.update_dataset(dataset["id"], private=False)

            return {
                "success": True,
                "dataset": dataset,
                "resources": resources_created,
                "ckan_url": f"{self.ckan_url}/dataset/{dataset['name']}",
                "message": f'Campaign data published to CKAN: {dataset["name"]}',
            }

        except Exception as e:
            logger.error(f"Failed to publish campaign to CKAN: {e}")
            raise APIError(f"CKAN publication failed: {e}")

    def get_organization(self, org_id: str) -> Dict[str, Any]:
        """
        Get CKAN organization information.

        Args:
            org_id: Organization ID or name

        Returns:
            Organization information
        """
        try:
            response = self.session.get(
                f"{self.ckan_url}/api/3/action/organization_show", params={"id": org_id}, timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()

            if not result.get("success"):
                raise APIError(
                    f"CKAN organization retrieval failed: {result.get('error')}"
                )

            return cast(Dict[str, Any], result["result"])

        except requests.exceptions.RequestException as e:
            raise APIError(f"Failed to get CKAN organization: {e}")

    def list_organizations(self) -> List[Dict[str, Any]]:
        """
        List CKAN organizations.

        Returns:
            List of organization information
        """
        try:
            response = self.session.get(
                f"{self.ckan_url}/api/3/action/organization_list",
                params={"all_fields": True},
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()

            if not result.get("success"):
                raise APIError(
                    f"CKAN organization listing failed: {result.get('error')}"
                )

            return cast(List[Dict[str, Any]], result["result"])

        except requests.exceptions.RequestException as e:
            raise APIError(f"Failed to list CKAN organizations: {e}")
