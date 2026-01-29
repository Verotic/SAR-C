"""
Drift calculation API endpoints.
"""
import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, BackgroundTasks

from app.models.drift import DriftRequest, DriftResponse, ObjectType
from app.models.leeway_coefficients import get_leeway_coefficient, LEEWAY_COEFFICIENTS
from app.services.copernicus import get_copernicus_client
from app.services.monte_carlo import MonteCarloSimulator
from app.utils.geo import create_bounding_box

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/calculate", response_model=DriftResponse)
async def calculate_drift(request: DriftRequest):
    """
    Calculate the search area for a drifting object.
    
    This endpoint performs a Monte Carlo simulation to predict
    where a drifting object might be after a given time period.
    """
    logger.info(f"Calculating drift for LKP: ({request.lkp.lat}, {request.lkp.lon})")
    
    # Create bounding box for data download
    # Estimate max drift based on projection hours (rough estimate: 2 km/hour max)
    estimated_max_drift_km = request.projection_hours * 2
    bbox = create_bounding_box(
        request.lkp.lat,
        request.lkp.lon,
        estimated_max_drift_km + 20  # Add buffer
    )
    
    # Get Copernicus client
    client = get_copernicus_client()
    
    # Time range for data
    start_time = request.incident_time
    end_time = request.incident_time + timedelta(hours=request.projection_hours)
    
    # Try to get oceanographic data
    currents_data = None
    wind_data = None
    
    try:
        currents_data = client.get_currents_data(
            min_lat=bbox[0],
            max_lat=bbox[1],
            min_lon=bbox[2],
            max_lon=bbox[3],
            start_time=start_time,
            end_time=end_time
        )
    except Exception as e:
        logger.warning(f"Could not get currents data: {e}")
    
    try:
        wind_data = client.get_wind_data(
            min_lat=bbox[0],
            max_lat=bbox[1],
            min_lon=bbox[2],
            max_lon=bbox[3],
            start_time=start_time,
            end_time=end_time
        )
    except Exception as e:
        logger.warning(f"Could not get wind data: {e}")
    
    # Run simulation
    simulator = MonteCarloSimulator(
        currents_data=currents_data,
        wind_data=wind_data
    )
    
    result = simulator.run_simulation(
        start_lat=request.lkp.lat,
        start_lon=request.lkp.lon,
        start_time=request.incident_time,
        projection_hours=request.projection_hours,
        object_type=request.object_type,
        num_particles=request.num_particles
    )
    
    return DriftResponse(
        search_area=result.search_polygon,
        priority_zone=result.priority_polygon,
        estimated_drift_distance_km=result.mean_drift_km,
        confidence_level=0.80,
        calculation_time_seconds=result.simulation_time_seconds,
        particles_summary={
            "total_particles": request.num_particles,
            "projection_hours": request.projection_hours,
            "object_type": request.object_type.value
        }
    )


@router.get("/object-types")
async def get_object_types():
    """Get available object types and their leeway coefficients."""
    return {
        obj_type.value: {
            "name": coeff.name,
            "leeway_percent_min": coeff.leeway_percent_min * 100,
            "leeway_percent_max": coeff.leeway_percent_max * 100,
            "divergence_angle": coeff.divergence_angle,
            "description": coeff.description
        }
        for obj_type, coeff in LEEWAY_COEFFICIENTS.items()
    }


@router.post("/preview")
async def preview_drift(request: DriftRequest):
    """
    Quick preview calculation with fewer particles.
    Useful for real-time UI feedback.
    """
    # Use fewer particles for quick preview
    quick_request = DriftRequest(
        lkp=request.lkp,
        incident_time=request.incident_time,
        projection_hours=request.projection_hours,
        object_type=request.object_type,
        num_particles=200  # Reduced for speed
    )
    
    simulator = MonteCarloSimulator()
    result = simulator.run_simulation(
        start_lat=quick_request.lkp.lat,
        start_lon=quick_request.lkp.lon,
        start_time=quick_request.incident_time,
        projection_hours=quick_request.projection_hours,
        object_type=quick_request.object_type,
        num_particles=quick_request.num_particles
    )
    
    return {
        "preview": True,
        "search_area": result.search_polygon,
        "estimated_drift_km": result.mean_drift_km,
        "stranded_particles": result.stranded_particle_count
    }
