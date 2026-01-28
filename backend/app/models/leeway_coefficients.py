"""
Leeway coefficients for different object types.
Based on international SAR manuals and drift studies.
"""
from dataclasses import dataclass
from app.models.drift import ObjectType


@dataclass
class LeewayCoefficient:
    """Leeway coefficient for an object type."""
    object_type: ObjectType
    name: str
    leeway_percent_min: float  # Minimum % of wind speed
    leeway_percent_max: float  # Maximum % of wind speed
    divergence_angle: float    # Degrees of divergence from wind direction
    description: str


# Leeway coefficients based on SAR documentation
LEEWAY_COEFFICIENTS: dict[ObjectType, LeewayCoefficient] = {
    ObjectType.PERSON_IN_WATER_VERTICAL: LeewayCoefficient(
        object_type=ObjectType.PERSON_IN_WATER_VERTICAL,
        name="Pessoa na água (Vertical)",
        leeway_percent_min=0.005,
        leeway_percent_max=0.005,
        divergence_angle=15.0,
        description="Person floating vertically, minimal exposure to wind"
    ),
    ObjectType.PERSON_IN_WATER_SURVIVAL: LeewayCoefficient(
        object_type=ObjectType.PERSON_IN_WATER_SURVIVAL,
        name="Pessoa na água (Sobrevivência)",
        leeway_percent_min=0.011,
        leeway_percent_max=0.011,
        divergence_angle=20.0,
        description="Person in survival position, moderate wind exposure"
    ),
    ObjectType.LIFE_RAFT: LeewayCoefficient(
        object_type=ObjectType.LIFE_RAFT,
        name="Bote Salva-vidas (sem âncora)",
        leeway_percent_min=0.035,
        leeway_percent_max=0.050,
        divergence_angle=28.0,
        description="Life raft without sea anchor, high wind exposure"
    ),
    ObjectType.FISHING_BOAT: LeewayCoefficient(
        object_type=ObjectType.FISHING_BOAT,
        name="Barco de Pesca à deriva",
        leeway_percent_min=0.040,
        leeway_percent_max=0.040,
        divergence_angle=30.0,
        description="Drifting fishing vessel"
    ),
    ObjectType.KAYAK: LeewayCoefficient(
        object_type=ObjectType.KAYAK,
        name="Kayak",
        leeway_percent_min=0.010,
        leeway_percent_max=0.010,
        divergence_angle=15.0,
        description="Kayak or similar small craft"
    ),
    ObjectType.DEBRIS: LeewayCoefficient(
        object_type=ObjectType.DEBRIS,
        name="Destroços",
        leeway_percent_min=0.025,
        leeway_percent_max=0.040,
        divergence_angle=25.0,
        description="Floating debris or wreckage"
    ),
}


def get_leeway_coefficient(object_type: ObjectType) -> LeewayCoefficient:
    """Get the leeway coefficient for a given object type."""
    return LEEWAY_COEFFICIENTS.get(
        object_type, 
        LEEWAY_COEFFICIENTS[ObjectType.PERSON_IN_WATER_VERTICAL]
    )
