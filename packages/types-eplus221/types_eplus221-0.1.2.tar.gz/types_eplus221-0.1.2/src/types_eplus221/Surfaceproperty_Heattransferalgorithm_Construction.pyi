from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Surfaceproperty_Heattransferalgorithm_Construction(EpBunch):
    """Determines which Heat Balance Algorithm will be used for surfaces that have a specific type of construction"""

    Name: Annotated[str, Field()]

    Algorithm: Annotated[Literal['ConductionTransferFunction', 'MoisturePenetrationDepthConductionTransferFunction', 'ConductionFiniteDifference', 'CombinedHeatAndMoistureFiniteElement'], Field(default='ConductionTransferFunction')]

    Construction_Name: Annotated[str, Field(default=...)]