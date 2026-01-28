"""
Monte Carlo particle tracking simulation for drift prediction.
"""
import logging
import time
from datetime import datetime, timedelta
from typing import Optional, Tuple, List
from dataclasses import dataclass

import numpy as np
import xarray as xr
from scipy import ndimage
from shapely.geometry import MultiPoint, Polygon
from shapely.ops import unary_union

from app.models.drift import ObjectType, DriftResponse
from app.services.leeway import (
    calculate_leeway_velocity_with_noise,
    meters_per_second_to_degrees_per_hour
)

logger = logging.getLogger(__name__)


@dataclass
class Particle:
    """A particle representing a possible position of the drifting object."""
    lat: float
    lon: float
    

@dataclass
class SimulationResult:
    """Result of a Monte Carlo drift simulation."""
    final_positions: List[Tuple[float, float]]  # (lat, lon) pairs
    search_polygon: dict  # GeoJSON
    priority_polygon: dict  # GeoJSON (80% confidence)
    mean_drift_km: float
    simulation_time_seconds: float


class MonteCarloSimulator:
    """Monte Carlo particle tracking simulator for drift prediction."""
    
    def __init__(
        self,
        currents_data: Optional[xr.Dataset] = None,
        wind_data: Optional[xr.Dataset] = None
    ):
        """
        Initialize the simulator with oceanographic data.
        
        Args:
            currents_data: xarray Dataset with 'uo' and 'vo' variables
            wind_data: xarray Dataset with wind velocity variables
        """
        self.currents_data = currents_data
        self.wind_data = wind_data
    
    def run_simulation(
        self,
        start_lat: float,
        start_lon: float,
        start_time: datetime,
        projection_hours: int,
        object_type: ObjectType,
        num_particles: int = 1000,
        time_step_hours: float = 1.0
    ) -> SimulationResult:
        """
        Run Monte Carlo drift simulation.
        
        Args:
            start_lat, start_lon: Starting position (LKP)
            start_time: Time of the incident
            projection_hours: Hours to project forward
            object_type: Type of drifting object
            num_particles: Number of particles to simulate
            time_step_hours: Time step for simulation in hours
            
        Returns:
            SimulationResult with final positions and polygons
        """
        sim_start = time.time()
        logger.info(f"Starting Monte Carlo simulation with {num_particles} particles")
        
        rng = np.random.default_rng()
        
        # Initialize particles at starting position with small initial spread
        initial_spread = 0.001  # ~100m spread
        particles_lat = np.full(num_particles, start_lat) + rng.normal(0, initial_spread, num_particles)
        particles_lon = np.full(num_particles, start_lon) + rng.normal(0, initial_spread, num_particles)
        
        # Number of time steps
        num_steps = int(projection_hours / time_step_hours)
        current_time = start_time
        
        # Run simulation
        for step in range(num_steps):
            # Get environmental data for current time
            current_u, current_v = self._get_current_at_time(current_time, particles_lat, particles_lon)
            wind_u, wind_v = self._get_wind_at_time(current_time, particles_lat, particles_lon)
            
            # Update each particle
            for i in range(num_particles):
                # Calculate velocity with noise
                vel_u, vel_v = calculate_leeway_velocity_with_noise(
                    current_u[i] if isinstance(current_u, np.ndarray) else current_u,
                    current_v[i] if isinstance(current_v, np.ndarray) else current_v,
                    wind_u[i] if isinstance(wind_u, np.ndarray) else wind_u,
                    wind_v[i] if isinstance(wind_v, np.ndarray) else wind_v,
                    object_type,
                    rng=rng
                )
                
                # Convert velocity to position change
                delta_lon, delta_lat = meters_per_second_to_degrees_per_hour(
                    vel_u, vel_v, particles_lat[i]
                )
                
                # Update position
                particles_lat[i] += delta_lat * time_step_hours
                particles_lon[i] += delta_lon * time_step_hours
            
            current_time += timedelta(hours=time_step_hours)
        
        # Calculate results
        final_positions = list(zip(particles_lat, particles_lon))
        
        # Calculate polygons
        search_polygon = self._create_convex_hull(final_positions)
        priority_polygon = self._create_density_polygon(final_positions, confidence=0.80)
        
        # Calculate mean drift distance
        mean_drift_km = self._calculate_mean_drift(
            start_lat, start_lon, particles_lat, particles_lon
        )
        
        sim_time = time.time() - sim_start
        logger.info(f"Simulation completed in {sim_time:.2f} seconds")
        
        return SimulationResult(
            final_positions=final_positions,
            search_polygon=search_polygon,
            priority_polygon=priority_polygon,
            mean_drift_km=mean_drift_km,
            simulation_time_seconds=sim_time
        )
    
    def _get_current_at_time(
        self,
        time: datetime,
        lats: np.ndarray,
        lons: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Get current velocity at given positions and time."""
        if self.currents_data is None:
            # Return default values if no data available
            return np.zeros_like(lats), np.zeros_like(lons)
        
        try:
            # Interpolate current data to particle positions
            ds = self.currents_data.sel(time=time, method='nearest')
            
            # Get mean values for the area as fallback
            mean_u = float(ds['uo'].mean())
            mean_v = float(ds['vo'].mean())
            
            return np.full_like(lats, mean_u), np.full_like(lons, mean_v)
            
        except Exception as e:
            logger.warning(f"Failed to get current data: {e}")
            return np.zeros_like(lats), np.zeros_like(lons)
    
    def _get_wind_at_time(
        self,
        time: datetime,
        lats: np.ndarray,
        lons: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Get wind velocity at given positions and time."""
        if self.wind_data is None:
            # Return default moderate wind if no data
            default_wind = 5.0  # m/s
            return np.full_like(lats, default_wind * 0.5), np.full_like(lons, default_wind * 0.5)
        
        try:
            ds = self.wind_data.sel(time=time, method='nearest')
            
            # Try different variable names
            wind_u_var = 'eastward_wind' if 'eastward_wind' in ds else 'u10'
            wind_v_var = 'northward_wind' if 'northward_wind' in ds else 'v10'
            
            mean_u = float(ds[wind_u_var].mean())
            mean_v = float(ds[wind_v_var].mean())
            
            return np.full_like(lats, mean_u), np.full_like(lons, mean_v)
            
        except Exception as e:
            logger.warning(f"Failed to get wind data: {e}")
            return np.full_like(lats, 2.5), np.full_like(lons, 2.5)
    
    def _create_convex_hull(self, positions: List[Tuple[float, float]]) -> dict:
        """Create a GeoJSON polygon from the convex hull of positions."""
        points = MultiPoint([(lon, lat) for lat, lon in positions])
        hull = points.convex_hull
        
        if isinstance(hull, Polygon):
            coords = [list(hull.exterior.coords)]
        else:
            # Handle edge cases
            coords = [[]]
            
        return {
            "type": "Polygon",
            "coordinates": coords
        }
    
    def _create_density_polygon(
        self,
        positions: List[Tuple[float, float]],
        confidence: float = 0.80
    ) -> dict:
        """Create a polygon containing the specified percentage of particles."""
        lats = np.array([p[0] for p in positions])
        lons = np.array([p[1] for p in positions])
        
        # Calculate center
        center_lat = np.mean(lats)
        center_lon = np.mean(lons)
        
        # Calculate distances from center
        distances = np.sqrt((lats - center_lat)**2 + (lons - center_lon)**2)
        
        # Find radius containing 80% of particles
        sorted_distances = np.sort(distances)
        confidence_index = int(len(sorted_distances) * confidence)
        radius = sorted_distances[confidence_index]
        
        # Create circular polygon
        angles = np.linspace(0, 2*np.pi, 32)
        polygon_lons = center_lon + radius * np.cos(angles)
        polygon_lats = center_lat + radius * np.sin(angles)
        
        coords = [list(zip(polygon_lons, polygon_lats))]
        
        return {
            "type": "Polygon",
            "coordinates": coords
        }
    
    def _calculate_mean_drift(
        self,
        start_lat: float,
        start_lon: float,
        end_lats: np.ndarray,
        end_lons: np.ndarray
    ) -> float:
        """Calculate mean drift distance in kilometers."""
        # Haversine formula
        R = 6371  # Earth's radius in km
        
        lat1 = np.radians(start_lat)
        lat2 = np.radians(end_lats)
        dlat = lat2 - lat1
        dlon = np.radians(end_lons - start_lon)
        
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        
        distances = R * c
        return float(np.mean(distances))
