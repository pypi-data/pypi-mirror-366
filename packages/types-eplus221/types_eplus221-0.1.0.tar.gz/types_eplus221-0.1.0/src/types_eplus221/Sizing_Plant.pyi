from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Sizing_Plant(EpBunch):
    """Specifies the input needed to autosize plant loop flow rates and equipment capacities."""

    Plant_Or_Condenser_Loop_Name: Annotated[str, Field(default=...)]
    """Enter the name of a PlantLoop or a CondenserLoop object"""

    Loop_Type: Annotated[Literal['Heating', 'Cooling', 'Condenser', 'Steam'], Field(default=...)]

    Design_Loop_Exit_Temperature: Annotated[float, Field(default=...)]

    Loop_Design_Temperature_Difference: Annotated[float, Field(default=..., gt=0.0)]

    Sizing_Option: Annotated[Literal['Coincident', 'NonCoincident'], Field(default='NonCoincident')]
    """if Coincident is chosen, then sizing is based on HVAC Sizing Simulations and"""

    Zone_Timesteps_In_Averaging_Window: Annotated[int, Field(ge=1, default=1)]
    """this is used in the coincident sizing algorithm to apply a running average to peak flow rates"""

    Coincident_Sizing_Factor_Mode: Annotated[Literal['None', 'GlobalHeatingSizingFactor', 'GlobalCoolingSizingFactor', 'LoopComponentSizingFactor'], Field()]
    """this is used to adjust the result for coincident sizing by applying a sizing factor"""