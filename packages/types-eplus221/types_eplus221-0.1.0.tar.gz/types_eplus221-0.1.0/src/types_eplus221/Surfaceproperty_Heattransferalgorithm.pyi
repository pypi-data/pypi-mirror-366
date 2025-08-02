from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Surfaceproperty_Heattransferalgorithm(EpBunch):
    """Determines which Heat Balance Algorithm will be used for a specific surface"""

    Surface_Name: Annotated[str, Field(default=...)]

    Algorithm: Annotated[Literal['ConductionTransferFunction', 'MoisturePenetrationDepthConductionTransferFunction', 'ConductionFiniteDifference', 'CombinedHeatAndMoistureFiniteElement'], Field(default='ConductionTransferFunction')]