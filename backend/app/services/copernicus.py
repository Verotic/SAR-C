"""
Copernicus Marine Service client for downloading oceanographic data.
"""
import os
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

import xarray as xr
import numpy as np

from app.config import get_settings

logger = logging.getLogger(__name__)

# Product IDs from Copernicus Marine Service
CURRENTS_PRODUCT_ID = "cmems_mod_glo_phy-cur_anfc_0.083deg_PT6H-i"
WIND_PRODUCT_ID = "cmems_obs-wind_glo_phy_nrt_l4_0.125deg_PT1H"


class CopernicusClient:
    """Client for interacting with Copernicus Marine Service API."""
    
    def __init__(self):
        self.settings = get_settings()
        self.cache_dir = Path(self.settings.data_cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._logged_in = False
    
    def _ensure_login(self) -> bool:
        """Ensure we are logged into Copernicus Marine Service."""
        if self._logged_in:
            return True
        
        try:
            import copernicusmarine
            
            # Try to login with credentials
            if self.settings.copernicus_username and self.settings.copernicus_password:
                result = copernicusmarine.login(
                    username=self.settings.copernicus_username,
                    password=self.settings.copernicus_password
                )
                if result:
                    self._logged_in = True
                    logger.info("Successfully logged into Copernicus Marine Service")
                    return True
                else:
                    logger.error("Copernicus login returned False - check credentials")
                    return False
            else:
                logger.warning("Copernicus credentials not configured")
                return False
                
        except Exception as e:
            logger.error(f"Failed to login to Copernicus: {e}")
            return False
    
    def get_currents_data(
        self,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float,
        start_time: datetime,
        end_time: datetime,
        use_cache: bool = True
    ) -> Optional[xr.Dataset]:
        """
        Download ocean currents data (uo, vo) for the specified area and time.
        
        Args:
            min_lat, max_lat: Latitude bounds
            min_lon, max_lon: Longitude bounds
            start_time, end_time: Time range
            use_cache: Whether to use cached data if available
            
        Returns:
            xarray Dataset with 'uo' (eastward) and 'vo' (northward) current velocities
        """
        cache_file = self._get_cache_path("currents", min_lat, max_lat, min_lon, max_lon, start_time, end_time)
        
        if use_cache and cache_file.exists():
            logger.info(f"Loading currents data from cache: {cache_file}")
            return xr.open_dataset(cache_file)
        
        if not self._ensure_login():
            logger.error("Cannot download data: not logged in")
            return None
        
        try:
            import copernicusmarine
            
            logger.info(f"Downloading currents data for area ({min_lat:.2f}, {min_lon:.2f}) to ({max_lat:.2f}, {max_lon:.2f})")
            
            ds = copernicusmarine.open_dataset(
                dataset_id=CURRENTS_PRODUCT_ID,
                variables=["uo", "vo"],
                minimum_latitude=min_lat,
                maximum_latitude=max_lat,
                minimum_longitude=min_lon,
                maximum_longitude=max_lon,
                start_datetime=start_time.isoformat(),
                end_datetime=end_time.isoformat(),
                minimum_depth=0,
                maximum_depth=1
            )
            
            # Cache the data
            ds.to_netcdf(cache_file)
            logger.info(f"Currents data cached to: {cache_file}")
            
            return ds
            
        except Exception as e:
            logger.error(f"Failed to download currents data: {e}")
            return None
    
    def get_wind_data(
        self,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float,
        start_time: datetime,
        end_time: datetime,
        use_cache: bool = True
    ) -> Optional[xr.Dataset]:
        """
        Download wind data (eastward_wind, northward_wind) for the specified area and time.
        
        Args:
            min_lat, max_lat: Latitude bounds
            min_lon, max_lon: Longitude bounds
            start_time, end_time: Time range
            use_cache: Whether to use cached data if available
            
        Returns:
            xarray Dataset with wind velocity components
        """
        cache_file = self._get_cache_path("wind", min_lat, max_lat, min_lon, max_lon, start_time, end_time)
        
        if use_cache and cache_file.exists():
            logger.info(f"Loading wind data from cache: {cache_file}")
            return xr.open_dataset(cache_file)
        
        if not self._ensure_login():
            logger.error("Cannot download data: not logged in")
            return None
        
        try:
            import copernicusmarine
            
            logger.info(f"Downloading wind data for area ({min_lat:.2f}, {min_lon:.2f}) to ({max_lat:.2f}, {max_lon:.2f})")
            
            ds = copernicusmarine.open_dataset(
                dataset_id=WIND_PRODUCT_ID,
                variables=["eastward_wind", "northward_wind"],
                minimum_latitude=min_lat,
                maximum_latitude=max_lat,
                minimum_longitude=min_lon,
                maximum_longitude=max_lon,
                start_datetime=start_time.isoformat(),
                end_datetime=end_time.isoformat()
            )
            
            # Cache the data
            ds.to_netcdf(cache_file)
            logger.info(f"Wind data cached to: {cache_file}")
            
            return ds
            
        except Exception as e:
            logger.error(f"Failed to download wind data: {e}")
            return None
    
    def _get_cache_path(
        self,
        data_type: str,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float,
        start_time: datetime,
        end_time: datetime
    ) -> Path:
        """Generate a cache file path for the given parameters."""
        filename = f"{data_type}_{min_lat:.2f}_{max_lat:.2f}_{min_lon:.2f}_{max_lon:.2f}_{start_time.strftime('%Y%m%d%H')}_{end_time.strftime('%Y%m%d%H')}.nc"
        return self.cache_dir / filename


# Singleton instance
_copernicus_client: Optional[CopernicusClient] = None


def get_copernicus_client() -> CopernicusClient:
    """Get the singleton Copernicus client instance."""
    global _copernicus_client
    if _copernicus_client is None:
        _copernicus_client = CopernicusClient()
    return _copernicus_client
