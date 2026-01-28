"""
Leeway drift model implementation.
Calculates the velocity of a drifting object based on ocean currents and wind.
"""
import numpy as np
from typing import Tuple

from app.models.drift import ObjectType
from app.models.leeway_coefficients import get_leeway_coefficient


def calculate_leeway_velocity(
    current_u: float,
    current_v: float,
    wind_u: float,
    wind_v: float,
    object_type: ObjectType,
    divergence_direction: int = 0
) -> Tuple[float, float]:
    """
    Calculate the drift velocity of an object based on currents and wind.
    
    The leeway formula is:
    V_obj = V_current + (L × W_wind) + Uncertainty
    
    Where:
    - V_current: Ocean current velocity vector
    - W_wind: Wind velocity vector  
    - L: Leeway coefficient (percentage of wind speed)
    
    Args:
        current_u: Eastward current velocity (m/s)
        current_v: Northward current velocity (m/s)
        wind_u: Eastward wind velocity (m/s)
        wind_v: Northward wind velocity (m/s)
        object_type: Type of object being tracked
        divergence_direction: -1 for left, 0 for straight, 1 for right divergence
        
    Returns:
        Tuple of (u, v) velocity components in m/s
    """
    coeff = get_leeway_coefficient(object_type)
    
    # Get average leeway percentage
    leeway_pct = (coeff.leeway_percent_min + coeff.leeway_percent_max) / 2
    
    # Calculate wind speed and direction
    wind_speed = np.sqrt(wind_u**2 + wind_v**2)
    wind_direction = np.arctan2(wind_v, wind_u)  # radians
    
    # Calculate leeway velocity magnitude
    leeway_speed = wind_speed * leeway_pct
    
    # Apply divergence angle
    divergence_rad = np.radians(coeff.divergence_angle * divergence_direction)
    leeway_direction = wind_direction + divergence_rad
    
    # Convert leeway velocity to components
    leeway_u = leeway_speed * np.cos(leeway_direction)
    leeway_v = leeway_speed * np.sin(leeway_direction)
    
    # Total velocity = current + leeway
    total_u = current_u + leeway_u
    total_v = current_v + leeway_v
    
    return (total_u, total_v)


def calculate_leeway_velocity_with_noise(
    current_u: float,
    current_v: float,
    wind_u: float,
    wind_v: float,
    object_type: ObjectType,
    current_noise_std: float = 0.05,
    wind_noise_std: float = 0.1,
    rng: np.random.Generator = None
) -> Tuple[float, float]:
    """
    Calculate drift velocity with added uncertainty for Monte Carlo simulation.
    
    Args:
        current_u, current_v: Ocean current velocity components (m/s)
        wind_u, wind_v: Wind velocity components (m/s)
        object_type: Type of object
        current_noise_std: Standard deviation for current noise (fraction)
        wind_noise_std: Standard deviation for wind noise (fraction)
        rng: Random number generator
        
    Returns:
        Tuple of (u, v) velocity components with added noise
    """
    if rng is None:
        rng = np.random.default_rng()
    
    coeff = get_leeway_coefficient(object_type)
    
    # Add noise to current
    noisy_current_u = current_u * (1 + rng.normal(0, current_noise_std))
    noisy_current_v = current_v * (1 + rng.normal(0, current_noise_std))
    
    # Add noise to wind
    noisy_wind_u = wind_u * (1 + rng.normal(0, wind_noise_std))
    noisy_wind_v = wind_v * (1 + rng.normal(0, wind_noise_std))
    
    # Randomly select divergence direction
    divergence_direction = rng.choice([-1, 0, 1])
    
    # Vary leeway coefficient within its range
    leeway_pct = rng.uniform(coeff.leeway_percent_min, coeff.leeway_percent_max)
    
    # Calculate wind contribution
    wind_speed = np.sqrt(noisy_wind_u**2 + noisy_wind_v**2)
    wind_direction = np.arctan2(noisy_wind_v, noisy_wind_u)
    
    leeway_speed = wind_speed * leeway_pct
    divergence_rad = np.radians(coeff.divergence_angle * divergence_direction)
    leeway_direction = wind_direction + divergence_rad
    
    leeway_u = leeway_speed * np.cos(leeway_direction)
    leeway_v = leeway_speed * np.sin(leeway_direction)
    
    return (noisy_current_u + leeway_u, noisy_current_v + leeway_v)


def meters_per_second_to_degrees_per_hour(
    velocity_u: float,
    velocity_v: float,
    latitude: float
) -> Tuple[float, float]:
    """
    Convert velocity from m/s to degrees per hour.
    
    Args:
        velocity_u: Eastward velocity in m/s
        velocity_v: Northward velocity in m/s
        latitude: Current latitude (for longitude correction)
        
    Returns:
        Tuple of (delta_lon, delta_lat) in degrees per hour
    """
    # Earth's radius in meters
    EARTH_RADIUS = 6371000
    
    # Meters per degree latitude (constant)
    meters_per_deg_lat = (2 * np.pi * EARTH_RADIUS) / 360
    
    # Meters per degree longitude (varies with latitude)
    meters_per_deg_lon = meters_per_deg_lat * np.cos(np.radians(latitude))
    
    # Convert m/s to degrees/hour
    # 1 hour = 3600 seconds
    delta_lat_per_hour = (velocity_v * 3600) / meters_per_deg_lat
    delta_lon_per_hour = (velocity_u * 3600) / meters_per_deg_lon if meters_per_deg_lon > 0 else 0
    
    return (delta_lon_per_hour, delta_lat_per_hour)
