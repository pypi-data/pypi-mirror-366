from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Coilsystem_Cooling_Dx_Heatexchangerassisted(EpBunch):
    """Virtual component consisting of a direct expansion (DX) cooling coil and an"""

    Name: Annotated[str, Field(default=...)]

    Heat_Exchanger_Object_Type: Annotated[Literal['HeatExchanger:AirToAir:FlatPlate', 'HeatExchanger:AirToAir:SensibleAndLatent', 'HeatExchanger:Desiccant:BalancedFlow'], Field(default=...)]

    Heat_Exchanger_Name: Annotated[str, Field(default=...)]

    Cooling_Coil_Object_Type: Annotated[Literal['Coil:Cooling:DX:SingleSpeed', 'Coil:Cooling:DX:VariableSpeed'], Field(default=...)]

    Cooling_Coil_Name: Annotated[str, Field(default=...)]