"""
Pydantic models for drift calculation.
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class ObjectType(str, Enum):
    """Types of objects that can be tracked for SAR operations."""
    PERSON_IN_WATER_VERTICAL = "person_in_water_vertical"
    PERSON_IN_WATER_SURVIVAL = "person_in_water_survival"
    LIFE_RAFT = "life_raft"
    FISHING_BOAT = "fishing_boat"
    KAYAK = "kayak"
    DEBRIS = "debris"


class Coordinate(BaseModel):
    """Geographic coordinate."""
    lat: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees")
    lon: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees")


class DriftRequest(BaseModel):
    """Request model for drift calculation."""
    lkp: Coordinate = Field(..., description="Last Known Position")
    incident_time: datetime = Field(..., description="Time of the incident")
    projection_hours: int = Field(
        default=24, 
        ge=1, 
        le=72, 
        description="Hours to project forward"
    )
    object_type: ObjectType = Field(
        default=ObjectType.PERSON_IN_WATER_VERTICAL,
        description="Type of object being searched"
    )
    num_particles: int = Field(
        default=1000,
        ge=100,
        le=5000,
        description="Number of particles for Monte Carlo simulation"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "lkp": {"lat": 38.7223, "lon": -9.1393},
                "incident_time": "2025-12-06T12:00:00Z",
                "projection_hours": 24,
                "object_type": "person_in_water_vertical",
                "num_particles": 1000
            }
        }


class DriftResponse(BaseModel):
    """Response model for drift calculation."""
    search_area: dict = Field(..., description="GeoJSON Polygon of total search area")
    priority_zone: dict = Field(..., description="GeoJSON Polygon of priority zone (80% confidence)")
    estimated_drift_distance_km: float = Field(..., description="Estimated drift distance in kilometers")
    confidence_level: float = Field(..., description="Confidence level (0-1)")
    calculation_time_seconds: float = Field(..., description="Time taken for calculation")
    particles_summary: dict = Field(..., description="Summary of particle distribution")


class DataBoundingBox(BaseModel):
    """Bounding box for data requests."""
    min_lat: float = Field(..., ge=-90, le=90)
    max_lat: float = Field(..., ge=-90, le=90)
    min_lon: float = Field(..., ge=-180, le=180)
    max_lon: float = Field(..., ge=-180, le=180)
    
    def to_tuple(self) -> tuple[float, float, float, float]:
        """Convert to tuple format (min_lon, min_lat, max_lon, max_lat)."""
        return (self.min_lon, self.min_lat, self.max_lon, self.max_lat)
