from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Heatbalancealgorithm(EpBunch):
    """Determines which Heat Balance Algorithm will be used ie."""

    Algorithm: Annotated[Literal['ConductionTransferFunction', 'MoisturePenetrationDepthConductionTransferFunction', 'ConductionFiniteDifference', 'CombinedHeatAndMoistureFiniteElement'], Field(default='ConductionTransferFunction')]

    Surface_Temperature_Upper_Limit: Annotated[float, Field(ge=200, default=200)]

    Minimum_Surface_Convection_Heat_Transfer_Coefficient_Value: Annotated[str, Field(default='0.1')]

    Maximum_Surface_Convection_Heat_Transfer_Coefficient_Value: Annotated[str, Field(default='1000')]