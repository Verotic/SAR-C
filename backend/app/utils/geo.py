"""
Geospatial utility functions.
"""
import math
from typing import Tuple


def haversine_distance(
    lat1: float, lon1: float,
    lat2: float, lon2: float
) -> float:
    """
    Calculate the great-circle distance between two points in kilometers.
    
    Args:
        lat1, lon1: First point coordinates in decimal degrees
        lat2, lon2: Second point coordinates in decimal degrees
        
    Returns:
        Distance in kilometers
    """
    R = 6371  # Earth's radius in km
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c


def create_bounding_box(
    center_lat: float,
    center_lon: float,
    radius_km: float
) -> Tuple[float, float, float, float]:
    """
    Create a bounding box around a center point.
    
    Args:
        center_lat, center_lon: Center coordinates
        radius_km: Radius in kilometers
        
    Returns:
        Tuple of (min_lat, max_lat, min_lon, max_lon)
    """
    # Approximate degrees per km
    km_per_deg_lat = 111.0
    km_per_deg_lon = 111.0 * math.cos(math.radians(center_lat))
    
    delta_lat = radius_km / km_per_deg_lat
    delta_lon = radius_km / km_per_deg_lon if km_per_deg_lon > 0 else radius_km / 111.0
    
    return (
        center_lat - delta_lat,
        center_lat + delta_lat,
        center_lon - delta_lon,
        center_lon + delta_lon
    )


def validate_coordinates(lat: float, lon: float) -> bool:
    """Check if coordinates are valid."""
    return -90 <= lat <= 90 and -180 <= lon <= 180
