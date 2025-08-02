from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Surfaceproperty_Heattransferalgorithm_Surfacelist(EpBunch):
    """Determines which Heat Balance Algorithm will be used for a list of surfaces"""

    Name: Annotated[str, Field(default=...)]

    Algorithm: Annotated[Literal['ConductionTransferFunction', 'MoisturePenetrationDepthConductionTransferFunction', 'ConductionFiniteDifference', 'CombinedHeatAndMoistureFiniteElement'], Field(default='ConductionTransferFunction')]

    Surface_Name_1: Annotated[str, Field(default=...)]

    Surface_Name_2: Annotated[str, Field()]

    Surface_Name_3: Annotated[str, Field()]

    Surface_Name_4: Annotated[str, Field()]

    Surface_Name_5: Annotated[str, Field()]

    Surface_Name_6: Annotated[str, Field()]