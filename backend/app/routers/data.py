"""
Copernicus data API endpoints.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.services.copernicus import get_copernicus_client
from app.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/status")
async def get_data_status():
    """Check Copernicus Marine Service connection status."""
    settings = get_settings()
    client = get_copernicus_client()
    
    return {
        "configured": bool(settings.copernicus_username),
        "cache_dir": str(settings.data_cache_dir),
        "cache_dir_exists": settings.data_cache_dir.exists()
    }


@router.get("/currents")
async def get_currents(
    min_lat: float = Query(..., ge=-90, le=90),
    max_lat: float = Query(..., ge=-90, le=90),
    min_lon: float = Query(..., ge=-180, le=180),
    max_lon: float = Query(..., ge=-180, le=180),
    start_time: Optional[datetime] = None,
    hours: int = Query(default=24, ge=1, le=72)
):
    """
    Get ocean currents data for the specified area.
    
    Returns metadata about the currents in the area.
    """
    if start_time is None:
        start_time = datetime.utcnow()
    
    end_time = start_time + timedelta(hours=hours)
    
    client = get_copernicus_client()
    
    try:
        data = client.get_currents_data(
            min_lat=min_lat,
            max_lat=max_lat,
            min_lon=min_lon,
            max_lon=max_lon,
            start_time=start_time,
            end_time=end_time
        )
        
        if data is None:
            return {
                "status": "unavailable",
                "message": "Could not retrieve currents data. Check Copernicus credentials."
            }
        
        # Calculate summary statistics
        mean_u = float(data['uo'].mean())
        mean_v = float(data['vo'].mean())
        
        return {
            "status": "available",
            "area": {
                "min_lat": min_lat,
                "max_lat": max_lat,
                "min_lon": min_lon,
                "max_lon": max_lon
            },
            "time_range": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat()
            },
            "summary": {
                "mean_eastward_velocity_ms": round(mean_u, 4),
                "mean_northward_velocity_ms": round(mean_v, 4),
                "mean_speed_ms": round((mean_u**2 + mean_v**2)**0.5, 4)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting currents data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/wind")
async def get_wind(
    min_lat: float = Query(..., ge=-90, le=90),
    max_lat: float = Query(..., ge=-90, le=90),
    min_lon: float = Query(..., ge=-180, le=180),
    max_lon: float = Query(..., ge=-180, le=180),
    start_time: Optional[datetime] = None,
    hours: int = Query(default=24, ge=1, le=72)
):
    """
    Get wind data for the specified area.
    
    Returns metadata about the wind in the area.
    """
    if start_time is None:
        start_time = datetime.utcnow()
    
    end_time = start_time + timedelta(hours=hours)
    
    client = get_copernicus_client()
    
    try:
        data = client.get_wind_data(
            min_lat=min_lat,
            max_lat=max_lat,
            min_lon=min_lon,
            max_lon=max_lon,
            start_time=start_time,
            end_time=end_time
        )
        
        if data is None:
            return {
                "status": "unavailable",
                "message": "Could not retrieve wind data. Check Copernicus credentials."
            }
        
        # Try different variable names
        wind_u_var = 'eastward_wind' if 'eastward_wind' in data else 'u10'
        wind_v_var = 'northward_wind' if 'northward_wind' in data else 'v10'
        
        mean_u = float(data[wind_u_var].mean())
        mean_v = float(data[wind_v_var].mean())
        
        return {
            "status": "available",
            "area": {
                "min_lat": min_lat,
                "max_lat": max_lat,
                "min_lon": min_lon,
                "max_lon": max_lon
            },
            "time_range": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat()
            },
            "summary": {
                "mean_eastward_velocity_ms": round(mean_u, 4),
                "mean_northward_velocity_ms": round(mean_v, 4),
                "mean_speed_ms": round((mean_u**2 + mean_v**2)**0.5, 4)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting wind data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
