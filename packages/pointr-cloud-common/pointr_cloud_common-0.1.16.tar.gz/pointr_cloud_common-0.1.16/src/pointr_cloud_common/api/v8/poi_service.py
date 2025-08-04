from typing import Dict, Any
import logging

from pointr_cloud_common.api.v8.base_service import BaseApiService


class PoiApiService(BaseApiService):
    """Service for POI related V8 API operations."""

    def __init__(self, api_service):
        super().__init__(api_service)
        self.logger = logging.getLogger(__name__)

    def get_level_pois(self, building_fid: str, level_index: str) -> Dict[str, Any]:
        """Return POIs for a specific level."""
        endpoint = f"api/v8/buildings/{building_fid}/levels/{level_index}/pois"
        return self._make_request("GET", endpoint)

    def delete_level_pois(self, building_fid: str, level_index: str) -> bool:
        """Delete all POIs for a specific level."""
        endpoint = f"api/v8/buildings/{building_fid}/levels/{level_index}/pois"
        self._make_request("DELETE", endpoint)
        return True

    def get_site_pois(self, site_fid: str) -> Dict[str, Any]:
        """Return POIs for a site."""
        endpoint = f"api/v8/sites/{site_fid}/pois"
        return self._make_request("GET", endpoint)

    def delete_site_pois(self, site_fid: str) -> bool:
        """Delete all POIs for a site."""
        endpoint = f"api/v8/sites/{site_fid}/pois"
        self._make_request("DELETE", endpoint)
        return True

    def get_site_pois_draft(self, site_fid: str) -> Dict[str, Any]:
        """Get draft POIs for a site."""
        endpoint = f"api/v8/sites/{site_fid}/pois/draft"
        return self._make_request("GET", endpoint)

    def get_level_pois_draft(self, building_fid: str, level_index: str) -> Dict[str, Any]:
        """Get draft POIs for a level."""
        endpoint = f"api/v8/buildings/{building_fid}/levels/{level_index}/pois/draft"
        return self._make_request("GET", endpoint)

    def delete_building_pois(self, building_fid: str) -> bool:
        """Delete all POIs for a building."""
        endpoint = f"api/v8/buildings/{building_fid}/pois"
        self._make_request("DELETE", endpoint)
        return True
