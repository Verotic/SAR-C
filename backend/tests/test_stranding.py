
import pytest
from datetime import datetime
import numpy as np
from app.services.monte_carlo import MonteCarloSimulator
from app.models.drift import ObjectType

def test_particle_stranding():
    """Test that particles stop when they hit land."""
    # Setup simulator with no external data (uses defaults)
    simulator = MonteCarloSimulator()
    
    # Define a start position in the sea near land (Lisbon coast)
    # Start slightly west of Lisbon
    start_lat = 38.70
    start_lon = -9.60 # Approx 30km offshore (water)
    
    # Mock wind to blow strong East (towards land)
    # 20 m/s East wind
    def mock_get_wind(time, lats, lons):
        return np.full_like(lats, 20.0), np.full_like(lons, 0.0)
        
    simulator._get_wind_at_time = mock_get_wind
    
    # Mock current to be zero
    simulator._get_current_at_time = lambda t, la, lo: (np.zeros_like(la), np.zeros_like(lo))
    
    # Run simulation
    # With 20 m/s wind, leeway is ~0.6 m/s ~ 2 km/h.
    # Distance ~15km. Should take ~7-8 hours.
    # Run for 24 hours to ensure impact.
    
    result = simulator.run_simulation(
        start_lat=start_lat,
        start_lon=start_lon,
        start_time=datetime.now(),
        projection_hours=24,
        object_type=ObjectType.PERSON_IN_WATER_SURVIVAL,
        num_particles=50
    )
    
    # Verify that particles were marked as stranded
    print(f"Stranded count: {result.stranded_particle_count}")
    assert result.stranded_particle_count > 0
    
    # Verify final positions are roughly at the coast (lon > -9.30)
    # Most should be around -9.2 to -9.15 (coastline)
    lons = [p[1] for p in result.final_positions]
    mean_lon = np.mean(lons)
    assert mean_lon > start_lon # They moved East
