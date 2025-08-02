from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Coilsystem_Cooling_Water_Heatexchangerassisted(EpBunch):
    """Virtual component consisting of a chilled-water cooling coil and an air-to-air heat"""

    Name: Annotated[str, Field(default=...)]

    Heat_Exchanger_Object_Type: Annotated[Literal['HeatExchanger:AirToAir:FlatPlate', 'HeatExchanger:AirToAir:SensibleAndLatent'], Field(default=...)]

    Heat_Exchanger_Name: Annotated[str, Field(default=...)]

    Cooling_Coil_Object_Type: Annotated[Literal['Coil:Cooling:Water', 'Coil:Cooling:Water:DetailedGeometry'], Field(default=...)]

    Cooling_Coil_Name: Annotated[str, Field(default=...)]