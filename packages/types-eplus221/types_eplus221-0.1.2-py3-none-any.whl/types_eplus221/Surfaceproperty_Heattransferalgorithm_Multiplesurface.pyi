from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Surfaceproperty_Heattransferalgorithm_Multiplesurface(EpBunch):
    """Determines which Heat Balance Algorithm will be used for a group of surface types"""

    Name: Annotated[str, Field(default=...)]

    Surface_Type: Annotated[Literal['AllExteriorSurfaces', 'AllExteriorWalls', 'AllExteriorRoofs', 'AllExteriorFloors', 'AllGroundContactSurfaces', 'AllInteriorSurfaces', 'AllInteriorWalls', 'AllInteriorCeilings', 'AllInteriorFloors'], Field(default=...)]

    Algorithm: Annotated[Literal['ConductionTransferFunction', 'MoisturePenetrationDepthConductionTransferFunction', 'ConductionFiniteDifference', 'CombinedHeatAndMoistureFiniteElement'], Field(default='ConductionTransferFunction')]