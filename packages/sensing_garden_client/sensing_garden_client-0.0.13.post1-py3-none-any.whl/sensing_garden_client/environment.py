"""
Environment operations for the Sensing Garden API.

This module provides functionality for creating and retrieving environmental readings.
"""
from typing import Dict, Optional, Any

from .client import BaseClient
from .shared import build_common_params


class EnvironmentClient:
    """Client for working with environmental readings in the Sensing Garden API."""

    def __init__(self, base_client: BaseClient):
        """
        Initialize the environment client.
        
        Args:
            base_client: The base client for API communication
        """
        self._client = base_client
    
    def add(
        self,
        device_id: str,
        data: Dict[str, float],
        timestamp: str,
        location: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Submit an environmental reading to the Sensing Garden API.
        
        Args:
            device_id: Unique identifier for the device
            data: Environmental sensor data with keys:
                - pm1p0: PM1.0 particulate matter reading (µg/m³)
                - pm2p5: PM2.5 particulate matter reading (µg/m³)
                - pm4p0: PM4.0 particulate matter reading (µg/m³)
                - pm10p0: PM10.0 particulate matter reading (µg/m³)
                - ambient_humidity: Ambient humidity percentage (%)
                - ambient_temperature: Ambient temperature (°C)
                - voc_index: Volatile Organic Compounds index
                - nox_index: Nitrogen Oxides index
            timestamp: Required ISO-8601 formatted timestamp
            location: Optional location data with keys 'lat', 'long', and optional 'alt'
            
        Returns:
            API response with the created environmental reading
            
        Raises:
            ValueError: If required parameters are invalid
            requests.HTTPError: For HTTP error responses
        """
        # Validate location data if provided
        if location is not None:
            if not isinstance(location, dict):
                raise ValueError("location must be a dictionary")
            
            required_location_keys = {'lat', 'long'}
            if not required_location_keys.issubset(location.keys()):
                raise ValueError("location must contain 'lat' and 'long' keys")
        
        # Validate environmental data
        if not isinstance(data, dict):
            raise ValueError("data must be a dictionary")
        
        required_data_keys = {
            'pm1p0', 'pm2p5', 'pm4p0', 'pm10p0',
            'ambient_humidity', 'ambient_temperature',
            'voc_index', 'nox_index'
        }
        if not required_data_keys.issubset(data.keys()):
            missing_keys = required_data_keys - data.keys()
            raise ValueError(f"data must contain all required keys. Missing: {missing_keys}")
        
        # Prepare payload
        payload = {
            "device_id": device_id,
            "data": data,
            "timestamp": timestamp
        }
        
        # Add location if provided
        if location is not None:
            payload["location"] = location
        
        # Make API request
        return self._client.post("environment", payload)
    
    def count(
        self,
        device_id: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> int:
        """
        Get the count of environmental readings matching the filter parameters.
        
        Args:
            device_id: Optional filter by device ID
            start_time: Optional start time for filtering (ISO-8601)
            end_time: Optional end time for filtering (ISO-8601)
            
        Returns:
            Integer count of matching environmental readings
            
        Raises:
            requests.HTTPError: For HTTP error responses
        """
        params = build_common_params(
            device_id=device_id,
            model_id=None,  # Not applicable for environmental readings
            start_time=start_time,
            end_time=end_time,
            limit=None, next_token=None, sort_by=None, sort_desc=None
        )
        resp = self._client.get("environment/count", params)
        return resp["count"]

    def fetch(
        self,
        device_id: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: int = 100,
        next_token: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_desc: bool = False
    ) -> Dict[str, Any]:
        """
        Retrieve environmental readings from the Sensing Garden API.
        
        Args:
            device_id: Optional filter by device ID
            start_time: Optional start time for filtering (ISO-8601)
            end_time: Optional end time for filtering (ISO-8601)
            limit: Maximum number of items to return
            next_token: Token for pagination
            sort_by: Attribute to sort by (e.g., 'timestamp')
            sort_desc: If True, sort in descending order, otherwise ascending
            
        Returns:
            API response with matching environmental readings
            
        Raises:
            requests.HTTPError: For HTTP error responses
        """
        # Build query parameters
        params = build_common_params(
            device_id=device_id,
            model_id=None,  # Not applicable for environmental readings
            start_time=start_time,
            end_time=end_time,
            limit=limit,
            next_token=next_token,
            sort_by=sort_by,
            sort_desc=sort_desc
        )
        
        # Make API request
        return self._client.get("environment", params)